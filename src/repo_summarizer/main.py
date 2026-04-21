"""
Repository Analysis Agent using OpenAI Agents SDK

Three-Agent System:
1. Navigator (Triage & Hierarchy) - Identifies the 'Logical Heart' of the codebase
2. Architect (Synthesis & Patterns) - Creates intelligence report from code
3. Guardrail (System Layer) - Privacy and Efficiency Monitor
"""

import os
import re
from typing import List, Dict, Any
from fnmatch import fnmatch
from pathlib import Path

from agents import Agent, Runner, function_tool, trace


# =============================================================================
# TOOLS FOR NAVIGATOR AGENT
# =============================================================================

def list_repo_files():
    """List all files in the repository, excluding binaries, assets, and lockfiles."""
    exclude_patterns = [
        '*.lock', '*.bin', '*.exe', '*.dll', '*.so', '*.dylib',
        '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.ico',
        '*.svg', '*.webp', '*.tiff', '*.woff', '*.woff2', '*.ttf', '*.eot',
        '.git/', '__pycache__/', '*.pyc', '*.pyo', '*~', '.DS_Store',
        '.venv/', 'venv/', 'node_modules/', '*.log', '*.tmp', '*.bak'
    ]

    all_files = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories except .git
        dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.git']

        for file in files:
            filepath = os.path.relpath(os.path.join(root, file), '.')

            # Check if file should be excluded
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern.endswith('/'):
                    if pattern.rstrip('/') in filepath:
                        should_exclude = True
                        break
                else:
                    if fnmatch(filepath, pattern) or file.endswith(pattern.lstrip('*')):
                        should_exclude = True
                        break

            if not should_exclude:
                all_files.append(filepath)

    return all_files


def get_file_size(filepath: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(filepath)


def identify_entry_points(file_list: List[str]) -> List[str]:
    """Identify potential entry point files."""
    entry_point_indicators = [
        '__init__.py', 'main.go', 'server.js', 'app.js', 'index.js',
        'main.py', 'main.ts', 'main.rs', 'Cargo.toml', 'package.json',
        'requirements.txt', 'setup.py', 'Dockerfile', 'docker-compose.yml',
        'Makefile', 'README.md', 'readme.md', 'Readme.md', 'pyproject.toml'
    ]

    entry_points = []
    for filepath in file_list:
        filename = os.path.basename(filepath).lower()
        if filename in [name.lower() for name in entry_point_indicators]:
            entry_points.append(filepath)

    return entry_points


def analyze_file_importance(filepath: str) -> int:
    """Rate importance of a file based on extension and name."""
    importance_score = 0

    high_importance_ext = ['.py', '.js', '.ts', '.go', '.rs', '.java', '.cpp', '.h', '.cs', '.rb', '.php']
    medium_importance_ext = ['.json', '.yaml', '.yml', '.xml', '.toml', '.cfg', '.conf', '.ini']

    _, ext = os.path.splitext(filepath)
    if ext.lower() in high_importance_ext:
        importance_score += 3
    elif ext.lower() in medium_importance_ext:
        importance_score += 2

    important_names = ['api', 'interface', 'router', 'config', 'schema', 'model', 'service', 'controller', 'route']
    filename = os.path.basename(filepath).lower().replace(ext.lower(), '')

    if any(imp_name in filename for imp_name in important_names):
        importance_score += 2

    important_dirs = ['src', 'lib', 'core', 'api', 'models', 'controllers', 'services', 'routes', 'handlers', 'utils']
    for dir_part in filepath.split(os.sep):
        if dir_part.lower() in important_dirs:
            importance_score += 1
            break

    return importance_score


def read_code_file(filepath: str, max_chars: int = 2000) -> str:
    """Read a code file, with optional character limit for large files."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(max_chars)
        return content
    except Exception as e:
        return f"// Error reading file: {str(e)}"


@function_tool
def scan_repository() -> Dict[str, Any]:
    """
    Navigator tool: Scan the repository and identify the 7 most important files.
    Returns a context packet with selected files and reasons for their importance.
    """
    print("🔍 Navigator: Scanning repository...")

    all_files = list_repo_files()
    print(f"   Found {len(all_files)} files")

    entry_points = identify_entry_points(all_files)
    print(f"   Identified {len(entry_points)} entry points")

    file_scores = [(filepath, analyze_file_importance(filepath)) for filepath in all_files]
    file_scores.sort(key=lambda x: x[1], reverse=True)

    selected_files = []
    for filepath, score in file_scores:
        if len(selected_files) >= 7:
            break
        try:
            if get_file_size(filepath) <= 50 * 1024:
                selected_files.append((filepath, score))
        except OSError:
            continue

    print(f"   Selected {len(selected_files)} files for analysis")

    context_packet = {
        "selected_files": [filepath for filepath, _ in selected_files],
        "reasons": {}
    }

    for filepath, score in selected_files:
        reasons = []
        _, ext = os.path.splitext(filepath)
        if ext.lower() in ['.py', '.js', '.ts', '.go', '.rs', '.java', '.cpp']:
            reasons.append("Contains primary application logic")
        if 'api' in filepath.lower() or 'interface' in filepath.lower():
            reasons.append("Defines API/interface contracts")
        if 'model' in filepath.lower() or 'schema' in filepath.lower():
            reasons.append("Defines data structures/types")
        if os.path.basename(filepath).lower() in ['__init__.py', 'main.py', 'server.js', 'app.js', 'index.js']:
            reasons.append("Entry point or initialization file")
        if 'config' in filepath.lower() or 'setting' in filepath.lower():
            reasons.append("Configuration file")

        context_packet["reasons"][filepath] = reasons

    return context_packet


@function_tool
def read_files(filepaths: List[str]) -> Dict[str, str]:
    """
    Navigator tool: Read content of specified files.
    Returns a dictionary mapping filepath to content.
    """
    print("📖 Navigator: Reading files...")
    files_content = {}
    for filepath in filepaths:
        print(f"   Reading {filepath}...")
        content = read_code_file(filepath)
        files_content[filepath] = content
    return files_content


# =============================================================================
# TOOLS FOR GUARDRAIL AGENT
# =============================================================================

@function_tool
def check_secrets(content: str) -> Dict[str, Any]:
    """
    Guardrail tool: Check content for privacy and efficiency concerns.
    Detects API keys, passwords, tokens, PII, and redacts them.
    """
    print("🛡️ Guardrail: Checking for secrets...")

    secret_patterns = [
        r'(?:^|[\s\'"])(?:API_KEY|SECRET|PASSWORD|TOKEN)[\s\'"]*[:=][\s\'"]*([^\s\'"\n]{8,})',
        r'(?:^|[\s\'"])(?:aws_access_key_id|aws_secret_access_key)[\s\'"]*[:=][\s\'"]*([^\s\'"\n]{10,})',
        r'(?:ssh-rsa|ssh-dss|ecdsa-sha2-nistp256)[\s]+[A-Za-z0-9+/]',
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        r'sk-[a-zA-Z0-9]{24}'
    ]

    redacted_content = content
    secrets_found = []

    for pattern in secret_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if len(match) > 5:
                secrets_found.append(match)
                redacted_content = redacted_content.replace(match, "[[SECURE_ERASURE]]")

    if secrets_found:
        print(f"   ⚠️ Found {len(secrets_found)} potential secrets - redacting")
    else:
        print("   ✅ No secrets detected")

    return {
        "redacted_content": redacted_content,
        "secrets_found": secrets_found,
        "is_clean": len(secrets_found) == 0
    }


# =============================================================================
# AGENT DEFINITIONS
# =============================================================================

navigator_agent = Agent(
    name="Navigator",
    instructions="""You are the Navigator agent. Your role is to perform high-level reconnaissance of the codebase.

Your responsibilities:
1. Use scan_repository() to discover all files and identify the 7 most important ones
2. Use read_files() to read the content of selected files
3. Return a structured context packet with:
   - selected_files: list of file paths
   - files_content: dictionary of filepath -> content
   - reasons: why each file was selected

Focus on finding files that reveal the architecture: entry points, configuration, core logic, API definitions, and data models.
""",
    tools=[scan_repository, read_files],
    model="gpt-4-turbo"
)


architect_agent = Agent(
    name="Architect",
    instructions="""You are the Principal Software Architect agent. Your role is to transform raw code into a high-density intelligence report.

Analyze the provided code files and produce a structured report with these exact headers:

🧩 System Architecture: Explain the high-level design and architectural pattern (Microservices, Monolithic, MVC, Event-driven, etc.)
⚙️ Functional Core: Describe the primary logic flows and how components interact
🛠️ Tech Stack & Utilities: Identify frameworks, libraries, and external integrations
⚠️ Risks & Technical Debt: Flag security risks, hardcoded secrets, complex code, or potential issues

Constraints:
- If you find credentials or PII (API Keys, Passwords, emails), replace them with [[SECURE_ERASURE]]
- Focus on production code, not test files
- Be concise but comprehensive
""",
    model="gpt-4-turbo"
)


guardrail_agent = Agent(
    name="Guardrail",
    instructions="""You are the Guardrail agent. Your role is to ensure security and privacy standards.

Your responsibilities:
1. Use check_secrets() to scan the Architect's report for any exposed credentials or PII
2. If secrets are found, ensure they are redacted with [[SECURE_ERASURE]]
3. Return the final sanitized report along with a security summary

Always output:
- final_report: The sanitized analysis report
- security_summary: Brief note on what was found and redacted (if anything)
""",
    tools=[check_secrets],
    model="gpt-4-turbo"
)


# =============================================================================
# ORCHESTRATION
# =============================================================================

async def run_analysis():
    """
    Main orchestration function that runs the three-agent pipeline.
    Navigator → Architect → Guardrail
    """
    print("🚀 Initializing Repository Analysis Agent")
    print("=" * 50)

    with trace("repository-analysis"):
        # Step 1: Navigator scans and reads files
        print("\n🧭 Phase 1: Navigator Reconnaissance")
        print("-" * 40)
        navigator_result = await Runner.run(
            navigator_agent,
            "Scan this repository and identify the 7 most important files. Then read their contents."
        )
        print(f"✅ Navigator completed")

        # Step 2: Architect analyzes the code
        print("\n🏗️ Phase 2: Architect Analysis")
        print("-" * 40)
        architect_result = await Runner.run(
            architect_agent,
            f"""Analyze the following code files and provide the intelligence report.

Context from Navigator:
{navigator_result.output}

Provide your analysis using the required headers:
🧩 System Architecture
⚙️ Functional Core
🛠️ Tech Stack & Utilities
⚠️ Risks & Technical Debt
"""
        )
        print(f"✅ Architect completed")

        # Step 3: Guardrail sanitizes the output
        print("\n🛡️ Phase 3: Guardrail Security Check")
        print("-" * 40)
        guardrail_result = await Runner.run(
            guardrail_agent,
            f"""Check the following analysis report for any exposed secrets, credentials, or PII.
Ensure everything is properly redacted.

Architect's Report:
{architect_result.output}

Return the sanitized final report with a security summary.
"""
        )
        print(f"✅ Guardrail completed")

    # Final Output
    print("\n" + "=" * 50)
    print("📊 FINAL ANALYSIS REPORT")
    print("=" * 50)
    print(guardrail_result.output)
    print("\n✨ Repository analysis complete!")

    return guardrail_result.output

def main():
    """Entry point for the CLI."""
    import asyncio

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY environment variable not set")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
        print("   Or create a .env file from .env.example")
        return

    print("🔑 OpenAI API key found")

    # Run the async analysis
    asyncio.run(run_analysis())


if __name__ == "__main__":
    main()

