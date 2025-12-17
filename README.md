# Auto-Claude: Autonomous Development Agent

A Python implementation of an autonomous coding agent powered by the Claude Agent SDK. This agent can autonomously build complete applications from specifications, managing its own progress across multiple sessions.

## Overview

This project implements a **two-agent pattern** for long-running autonomous development:

1. **Initializer Agent** (Session 1)
   - Reads application specification from `prompts/app_spec.txt`
   - Creates comprehensive test suite (`feature_list.json`) with 200+ test cases
   - Sets up project structure and environment scripts
   - Initializes git repository

2. **Coding Agent** (Sessions 2+)
   - Implements features incrementally
   - Tests through browser automation
   - Updates feature tracking
   - Commits progress to git

## Features

- 🤖 **Fully Autonomous**: Builds complete applications without human intervention
- 🔒 **Secure by Default**: Defense-in-depth security with sandbox isolation and command allowlists
- 📊 **Progress Tracking**: Persistent state management across sessions via `feature_list.json`
- 🔄 **Session Management**: Pause/resume at any time with automatic state recovery
- 🧪 **Comprehensive Testing**: Browser automation for real UI testing
- 📝 **Clear Documentation**: Auto-generated progress notes and git history

## Requirements

- **Python 3.10+** (tested with Python 3.13)
- **Claude Code CLI** (installed via npm)
- **Anthropic API Key**

## Installation

### 1. Install Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Set up Python Environment

```bash
# Create virtual environment (recommended)
python3.13 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set API Key

```bash
# Get your API key from https://console.anthropic.com/
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API key
```

## Usage

### Basic Usage

```bash
python autonomous_agent_demo.py --project-dir ./my_project
```

### With Limited Iterations (for testing)

```bash
python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 3
```

### Using a Different Model

```bash
python autonomous_agent_demo.py --project-dir ./my_project --model claude-opus-4-5-20250929
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project-dir` | Directory for the generated project | `./autonomous_demo_project` |
| `--max-iterations` | Maximum agent iterations (for testing) | Unlimited |
| `--model` | Claude model to use | `claude-sonnet-4-5-20250929` |

## Project Structure

```
auto-claude/
├── autonomous_agent_demo.py   # Main entry point
├── agent.py                   # Agent session logic
├── client.py                  # Claude SDK client configuration
├── security.py                # Bash command validation
├── progress.py                # Progress tracking utilities
├── prompts.py                 # Prompt loading utilities
├── prompts/
│   ├── app_spec.txt          # Application specification (customize this!)
│   ├── initializer_prompt.md # First session prompt
│   └── coding_prompt.md      # Continuation session prompt
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Generated Project Structure

When the agent runs, it creates a project with this structure:

```
my_project/
├── feature_list.json         # Test cases (source of truth)
├── app_spec.txt             # Copied specification
├── init.sh                  # Environment setup script
├── claude-progress.txt      # Session progress notes
├── .claude_settings.json    # Security settings
└── [application files]      # Generated application code
```

## Customization

### Change the Application

Edit `prompts/app_spec.txt` to specify what you want to build:

```bash
# Edit the specification
nano prompts/app_spec.txt
```

### Adjust Feature Count

For faster demos, edit `prompts/initializer_prompt.md` to create fewer test cases (e.g., 20-50 instead of 200+).

### Modify Allowed Commands

Edit `security.py` to add or remove allowed bash commands:

```python
ALLOWED_COMMANDS = {
    "ls", "cat", "grep",  # Add more commands here
    # ...
}
```

## Security Model

This project implements **defense-in-depth** security:

### 1. OS-Level Sandbox
- Bash commands run in an isolated environment
- File operations restricted to project directory

### 2. Permission System
- File reads/writes limited to project directory only
- Network access controlled
- Auto-approval for safe operations

### 3. Command Allowlist
Only these bash commands are permitted:
- **File inspection**: ls, cat, head, tail, wc, grep
- **File operations**: cp, mkdir, chmod (+x only)
- **Development**: npm, node, npx
- **Version control**: git
- **Process management**: ps, lsof, sleep, pkill (dev processes only)

## Timing Expectations

⚠️ **This demo takes time:**

- **First session**: 10-20+ minutes (generating 200+ test cases)
- **Subsequent sessions**: 5-15 minutes each
- **Complete application**: Many hours across multiple sessions

**Tip**: Use `--max-iterations 3` for quick testing

## Interrupting and Resuming

You can interrupt the agent at any time with `Ctrl+C`. To resume:

```bash
# Run the same command again
python autonomous_agent_demo.py --project-dir ./my_project
```

The agent will pick up where it left off using the persisted state in `feature_list.json`.

## Running the Generated Application

After the agent creates your application:

```bash
cd generations/my_project

# Run the setup script
./init.sh

# Or manually (typical for Node.js apps)
npm install
npm run dev
```

The application is typically available at `http://localhost:5173` or `http://localhost:3000`.

## Troubleshooting

### API Key Not Found

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

### Python Version Too Old

The SDK requires Python 3.10+. Check your version:

```bash
python3 --version
```

If needed, install a newer Python version or use the specific Python binary:

```bash
python3.13 autonomous_agent_demo.py --project-dir ./my_project
```

### Claude Code CLI Not Found

```bash
npm install -g @anthropic-ai/claude-code
```

### Permission Errors

If you see permission errors, the agent may be trying to access files outside the project directory. This is blocked by design for security.

## How It Works

### Session Flow

1. **Initialization**
   - Check if `feature_list.json` exists
   - If not, run initializer agent to set up project
   - If yes, run coding agent to continue work

2. **Agent Execution**
   - Agent receives appropriate prompt (initializer or coding)
   - Agent uses tools (Read, Write, Edit, Bash, etc.)
   - All bash commands validated against allowlist
   - Progress tracked in real-time

3. **Auto-Continue**
   - 3-second delay between sessions
   - Fresh context window for each session
   - State persisted via files and git

### Progress Tracking

Progress is tracked through:
- `feature_list.json`: Source of truth for test cases
- `claude-progress.txt`: Session notes
- Git commits: Version history
- File system: Generated application code

## Examples

### Quick Test Run

```bash
# Generate a small demo (3 iterations)
python autonomous_agent_demo.py \
  --project-dir ./quick_demo \
  --max-iterations 3
```

### Full Application Build

```bash
# Build complete application (will run for hours)
python autonomous_agent_demo.py \
  --project-dir ./my_full_app

# Let it run overnight or across multiple days
# Interrupt with Ctrl+C when needed
# Resume later with the same command
```

## Contributing

This is a demonstration project. Feel free to:
- Customize prompts for your use case
- Extend security allowlists as needed
- Add new tools or capabilities
- Improve error handling

## License

MIT License - see LICENSE file for details

## Acknowledgments

Based on the [autonomous-coding quickstart](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding) from Anthropic.

## Learn More

- [Claude Agent SDK Documentation](https://docs.claude.com/en/api/agent-sdk/overview)
- [Python SDK Reference](https://docs.claude.com/en/api/agent-sdk/python)
- [Claude Code](https://claude.com/claude-code)

---

**Happy Autonomous Coding!** 🤖✨
