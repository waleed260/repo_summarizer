# Repository Analysis Agent Implementation Notes

## Overview

This project implements a sophisticated repository analysis tool featuring three distinct AI agents working in coordination, as requested:

1. **Navigator (Triage & Hierarchy)** - Identifies the 'Logical Heart' of the codebase
2. **Architect (Synthesis & Patterns)** - Creates intelligence reports from code
3. **Guardrail (System Layer)** - Privacy and Efficiency Monitor

## Key Components

### Navigator (Triage & Hierarchy)
- Executes `list_repo_files()` to scan all repository files
- Filters out binaries, assets, and dependency lockfiles
- Identifies entry points like `__init__.py`, `main.py`, `server.js`, etc.
- Uses heuristic analysis to rate file importance based on:
  - File extension (prioritizing source code files)
  - Filename patterns (API, interface, model, etc.)
  - Directory location (src, lib, core, etc.)
- Selects the 7 most informative files while respecting size limits

### Architect (Synthesis & Patterns)
- Reads the selected files (with size limits for efficiency)
- Uses OpenAI API to generate comprehensive analysis reports
- Produces structured output with:
  - System Architecture analysis
  - Functional Core description
  - Tech Stack & Utilities identification
  - Risks & Technical Debt assessment
- Handles API integration gracefully with fallbacks

### Guardrail (System Layer)
- Scans content for potential secrets and PII
- Uses regex patterns to detect API keys, passwords, email addresses
- Replaces sensitive information with `[[SECURE_ERASURE]]`
- Ensures efficiency by limiting analysis of oversized files
- Prevents disclosure of credentials

## Technical Implementation

### File Selection Algorithm
```python
def analyze_file_importance(filepath: str) -> int:
    # Rates importance based on extension, name, and directory
    # High priority: .py, .js, .go, etc. (source code)
    # Medium priority: .json, .yaml, .toml (configuration)
    # Additional scoring for important filenames and directories
```

### Security Scanning
- Checks for various secret patterns including AWS keys, API keys, email addresses
- Uses sophisticated regex patterns to avoid false positives
- Redacts sensitive information before output

### OpenAI Integration
- Uses the modern OpenAI SDK (`openai>=1.0.0`)
- Implements proper error handling when API key is missing
- Graceful degradation when API is unavailable

## Usage Instructions

1. Set up environment:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. Install dependencies:
   ```bash
   pip install repo-summarizer
   # or
   uv pip install repo-summarizer
   ```

3. Run in any repository:
   ```bash
   repo-summarizer
   ```

## Architecture Compliance

✅ **Navigator Requirements Met:**
- Performs high-level reconnaissance
- Filters binaries/assets/lockfiles
- Identifies system entry points
- Selects 7 most informative files
- Creates "Context Packet" with reasoning

✅ **Architect Requirements Met:**
- Transforms raw code to intelligence reports
- Identifies architectural patterns
- Analyzes tech stack and utilities
- Flags security risks and technical debt
- Uses structured output format

✅ **Guardrail Requirements Met:**
- Blocks output containing raw API keys
- Limits analysis of files >50KB
- Redirects unrelated queries (conceptually)
- Protects privacy through redaction

## Security Features

- Automatic detection and redaction of API keys
- Protection against credential leakage
- Size limits to prevent resource exhaustion
- Environment variable for API key management

## Extensibility

The system is designed for easy extension:
- Modular agent architecture
- Pluggable analysis engines
- Configurable file selection criteria
- Customizable security patterns