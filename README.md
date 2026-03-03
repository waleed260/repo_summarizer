# Repository Analysis Agent

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-007bff.svg)](https://github.com/openai/openai-agents-python)

A sophisticated AI-powered repository analysis tool built with the **OpenAI Agents SDK**, employing a **three-agent pipeline** to understand, analyze, and report on codebase architecture, patterns, and security concerns.

---

## 🤖 The Three-Agent Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    REPOSITORY ANALYSIS                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  NAVIGATOR  │───▶│  ARCHITECT  │───▶│  GUARDRAIL  │         │
│  │  (Scan)     │    │  (Analyze)  │    │  (Secure)   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│       Agent              Agent            Agent                 │
│  tools: scan_         model:           tools: check_           │
│         read_files      gpt-4-turbo        secrets              │
└─────────────────────────────────────────────────────────────────┘
```

Built with the **OpenAI Agents SDK**, featuring:
- ✅ **Function Tools** - Agents call Python functions directly
- ✅ **Handoffs** - Clean agent-to-agent transfer via Runner
- ✅ **Guardrails** - Built-in input/output validation
- ✅ **Tracing** - Full observability with `trace()` context
- ✅ **Type Safety** - Full TypeScript-like type hints

---

## 🏗️ Agent Architecture

### 1. 🧭 Navigator Agent

**Role**: High-level reconnaissance of the codebase

**Tools**:
- `scan_repository()` - Discovers files, filters binaries/assets, selects top 7 by importance
- `read_files(filepaths)` - Reads content of selected files (max 2KB each)

**Output**: Context packet with selected files, content, and selection reasons

```python
navigator_agent = Agent(
    name="Navigator",
    instructions="Perform high-level reconnaissance...",
    tools=[scan_repository, read_files],
    model="gpt-4-turbo"
)
```

### 2. 🏗️ Architect Agent

**Role**: Transform raw code into intelligence reports

**Analysis Structure**:
```
🧩 System Architecture    → High-level design & patterns
⚙️ Functional Core         → Primary logic flows
🛠️ Tech Stack & Utilities → Frameworks & integrations
⚠️ Risks & Technical Debt → Security & complexity issues
```

```python
architect_agent = Agent(
    name="Architect",
    instructions="Transform raw code into intelligence reports...",
    model="gpt-4-turbo"
)
```

### 3. 🛡️ Guardrail Agent

**Role**: Security and privacy enforcement

**Tools**:
- `check_secrets(content)` - Detects API keys, passwords, tokens, PII; redacts with `[[SECURE_ERASURE]]`

**Detected Patterns**:
- API keys (`API_KEY`, `SECRET`, `PASSWORD`, `TOKEN`)
- AWS credentials (`aws_access_key_id`, `aws_secret_access_key`)
- SSH keys (`ssh-rsa`, `ssh-dss`)
- Email addresses (PII)
- OpenAI keys (`sk-[a-zA-Z0-9]{24}`)

```python
guardrail_agent = Agent(
    name="Guardrail",
    instructions="Ensure security and privacy standards...",
    tools=[check_secrets],
    model="gpt-4-turbo"
)
```

---

## 🛠️ Installation

### Using pip

```bash
pip install repo-summarizer
```

### Using uv (recommended)

```bash
uv pip install repo-summarizer
```

### From Source

```bash
git clone https://github.com/waleed260/repo-summarizer.git
cd repo-summarizer
uv install
```

---

## 🔑 Setup

### 1. Obtain an OpenAI API Key

Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 2. Configure Environment Variable

**Option A: Temporary**
```bash
export OPENAI_API_KEY='sk-...'
```

**Option B: Using .env file**
```bash
cp .env.example .env
# Edit .env with your key
```

---

## 🚀 Usage

### Command Line

```bash
repo-summarizer
```

### Python Module

```bash
python -m repo_summarizer
```

### Programmatic (Async)

```python
import asyncio
from repo_summarizer import run_analysis

async def main():
    report = await run_analysis()
    print(report)

asyncio.run(main())
```

### Programmatic (Agent Access)

```python
from repo_summarizer import navigator_agent, architect_agent, guardrail_agent
from agents import Runner

async def custom_pipeline():
    # Use agents individually
    nav_result = await Runner.run(navigator_agent, "Scan this repo")
    arch_result = await Runner.run(architect_agent, nav_result.output)
    guard_result = await Runner.run(guardrail_agent, arch_result.output)
    return guard_result.output
```

---

## 📊 Example Output

```
🚀 Initializing Repository Analysis Agent
==================================================
🔑 OpenAI API key found

🧭 Phase 1: Navigator Reconnaissance
----------------------------------------
🔍 Navigator: Scanning repository...
   Found 156 files
   Identified 12 entry points
   Selected 7 files for analysis
✅ Navigator completed

🏗️ Phase 2: Architect Analysis
----------------------------------------
✅ Architect completed

🛡️ Phase 3: Guardrail Security Check
----------------------------------------
🛡️ Guardrail: Checking for secrets...
   ✅ No secrets detected
✅ Guardrail completed

==================================================
📊 FINAL ANALYSIS REPORT
==================================================

🧩 System Architecture:
The system follows a modular three-agent architecture...

⚙️ Functional Core:
The Navigator performs file discovery and importance scoring...

🛠️ Tech Stack & Utilities:
- Python 3.12+
- OpenAI Agents SDK
- GPT-4-turbo model

⚠️ Risks & Technical Debt:
No critical issues detected. Consider adding unit tests...

✨ Repository analysis complete!
```

---

## 🔧 Orchestration Flow

```python
async def run_analysis():
    with trace("repository-analysis"):
        # Phase 1: Navigator
        navigator_result = await Runner.run(
            navigator_agent,
            "Scan this repository and identify the 7 most important files."
        )

        # Phase 2: Architect
        architect_result = await Runner.run(
            architect_agent,
            f"Analyze these files:\n{navigator_result.output}"
        )

        # Phase 3: Guardrail
        guardrail_result = await Runner.run(
            guardrail_agent,
            f"Check for secrets:\n{architect_result.output}"
        )

    return guardrail_result.output
```

---

## 🛡️ Security Features

| Feature | Description |
|---------|-------------|
| **Secret Detection** | Regex-based detection of API keys, passwords, tokens |
| **PII Protection** | Email addresses and personal info redacted |
| **Automatic Redaction** | All secrets replaced with `[[SECURE_ERASURE]]` |
| **Size Limits** | Files >50KB excluded; content limited to 2KB |
| **Environment Variables** | API keys stored securely, never in code |

---

## 📋 Features

- ✅ **OpenAI Agents SDK** - Built with official SDK for reliability
- ✅ **Three-Agent Pipeline** - Clean separation of concerns
- ✅ **Function Tools** - Agents call Python functions natively
- ✅ **Full Tracing** - Observability with `trace()` context manager
- ✅ **Multi-language** - Python, JS/TS, Go, Rust, Java, C++, etc.
- ✅ **Smart File Selection** - Heuristic importance scoring
- ✅ **Security First** - Automatic credential redaction
- ✅ **Cross-platform** - Linux, macOS, Windows

---

## 📁 Project Structure

```
repo_summarizer/
├── src/
│   └── repo_summarizer/
│       ├── __init__.py          # Package exports
│       └── main.py              # Agents & orchestration
├── tests/
│   └── test_package.py          # Test suite
├── .env.example                 # Environment template
├── pyproject.toml               # Project config
└── README.md                    # This file
```

---

## 🧪 Testing

```bash
# Run tests
python test_package.py

# Or with pytest
pytest test_package.py
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `openai-agents` | >=0.0.3 | OpenAI Agents SDK |
| `python-dotenv` | >=1.0.0 | Environment management |

---

## 🔌 Extending the System

### Add a New Tool

```python
@function_tool
def search_code(pattern: str) -> List[str]:
    """Search for code patterns across files."""
    ...

# Add to an agent
navigator_agent = Agent(
    name="Navigator",
    tools=[scan_repository, read_files, search_code],
    ...
)
```

### Add a New Agent

```python
reviewer_agent = Agent(
    name="Reviewer",
    instructions="Review code for best practices...",
    model="gpt-4-turbo"
)

# Use in pipeline
review_result = await Runner.run(reviewer_agent, architect_result.output)
```

### Custom Handoffs

```python
from agents import handoff

architect_agent = Agent(
    name="Architect",
    handoffs=[guardrail_agent],  # Can transfer to Guardrail
    ...
)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Built with [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- Powered by [OpenAI API](https://platform.openai.com/)
- Package management by [uv](https://github.com/astral-sh/uv)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/waleed260/repo-summarizer/issues)
- **Email**: vkdeku20@gmail.com

---

<div align="center">

**Repository Analysis Agent** - Built with OpenAI Agents SDK

*Understanding codebases, one repository at a time.*

</div>
