# Auto-Claude: Autonomous Development Agent

A Python implementation of an autonomous coding agent powered by the Claude Agent SDK. This agent can autonomously build complete applications from specifications, managing its own progress across multiple sessions.

## Overview

This project implements a **two-agent pattern** for long-running autonomous development:

1. **Initializer Agent** (Session 1)
   - Reads application specification from `prompts/app_spec.txt`
   - Creates comprehensive test suite (`feature_list.json`) with 40-50 detailed test cases
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
- **Authentication**: Either Claude Subscription (default) OR Anthropic API Key

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

### 3. Set Up Authentication

#### Option A: Claude Subscription (Default - Recommended)

Use your Claude Pro or Max subscription to power the agent:

```bash
# 1. Get your OAuth token (valid for 1 year)
claude setup-token

# 2. Copy the OAuth token from the output and set it as an environment variable
export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token-here'

# 3. (Optional) Add to your shell profile for persistence
echo 'export CLAUDE_CODE_OAUTH_TOKEN="your-oauth-token-here"' >> ~/.zshrc  # or ~/.bashrc
```

Or add to `.env` file:
```bash
cp .env.example .env
# Edit .env and add: CLAUDE_CODE_OAUTH_TOKEN=your-oauth-token-here
```

#### Option B: API Key

If you prefer to use an API key instead:

```bash
# Get your API key from https://console.anthropic.com/
export ANTHROPIC_API_KEY='your-api-key-here'

# Then use --auth-method api-key when running
python autonomous_agent_demo.py --project-dir ./my_app --auth-method api-key
```

## Usage

### Option 1: Create Spec First (Recommended for New Projects)

Let Claude help you create a comprehensive app specification:

```bash
# Interactive spec builder - Claude will ask questions and help refine your idea
python autonomous_agent_demo.py --create-spec --project-dir ./my_app

# Or use the standalone spec builder
python spec_builder.py
```

**What happens:**
1. You describe what you want to build
2. Claude asks 3-5 key clarifying questions about features, design, tech stack
3. You provide answers OR type 'done'/'skip' to generate spec immediately
4. Claude generates a comprehensive XML `app_spec.txt` in your project directory
5. You can review/edit it before the agent starts
6. Optionally proceed directly to autonomous development

**Conversation Options:**
- Answer Claude's questions normally
- Type `done` - Generate spec with current information
- Type `skip` - Skip remaining questions and generate spec immediately
- Maximum 6 conversation turns (prevents getting stuck)
- Automatic timeout after 120 seconds per response (prevents hanging)

**Need Help?** See [SPEC_BUILDER_TIPS.md](./docs/SPEC_BUILDER_TIPS.md) for troubleshooting and best practices.

### Option 2: Use Existing Spec

If you already have an `app_spec.txt`:

```bash
# Default - uses Claude subscription
python autonomous_agent_demo.py --project-dir ./my_project
```

### Using API Key Instead

```bash
python autonomous_agent_demo.py --project-dir ./my_project --auth-method api-key
```

### With Limited Iterations (for testing)

```bash
python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 3
```

### Using a Different Model

You can switch between Claude models for cost/performance tradeoffs:

```bash
# Haiku 3.5 - Fastest and cheapest (great for simple apps)
python autonomous_agent_demo.py --project-dir ./my_project --model claude-3-5-haiku-20241022

# Sonnet 4.5 - Balanced performance and cost (default, recommended)
python autonomous_agent_demo.py --project-dir ./my_project --model claude-sonnet-4-5-20250929

# Opus 4.5 - Most capable but expensive (complex apps only)
python autonomous_agent_demo.py --project-dir ./my_project --model claude-opus-4-5-20251101
```

**Model Comparison:**

| Model | Version | Speed | Cost | Best For |
|-------|---------|-------|------|----------|
| **Haiku** | 3.5 | ⚡⚡⚡ Fast | 💰 Cheap | Simple CRUD apps, prototypes, learning |
| **Sonnet** | 4.5 | ⚡⚡ Medium | 💰💰 Medium | Most production apps (default) |
| **Opus** | 4.5 | ⚡ Slower | 💰💰💰 Expensive | Complex apps, advanced features |

**💡 Cost Savings Tip:** Start with Haiku for initial development, then switch to Sonnet for polish:

```bash
# Phase 1: Fast initial development with Haiku 3.5
python autonomous_agent_demo.py --project-dir ./my_app --model claude-3-5-haiku-20241022 --max-iterations 5

# Phase 2: Polish and refine with Sonnet 4.5
python autonomous_agent_demo.py --project-dir ./my_app --model claude-sonnet-4-5-20250929
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project-dir` | Directory for the generated project | `./autonomous_demo_project` |
| `--create-spec` | Create app_spec.txt interactively before starting | `False` |
| `--spec-file` | Path to app specification file | `prompts/app_spec.txt` |
| `--max-iterations` | Maximum agent iterations (for testing) | Unlimited |
| `--model` | Claude model to use | `claude-sonnet-4-5-20250929` |
| `--auth-method` | Authentication method: `subscription` or `api-key` | `subscription` |

## Project Structure

```
auto-claude/
├── autonomous_agent_demo.py   # Main entry point
├── spec_builder.py            # Interactive spec builder (NEW!)
├── test_auth.py              # Authentication tester
├── agent.py                   # Agent session logic
├── client.py                  # Claude SDK client configuration
├── security.py                # Bash command validation
├── progress.py                # Progress tracking utilities
├── prompts.py                 # Prompt loading utilities
├── prompts/
│   ├── app_spec.txt          # Example specification (template)
│   ├── initializer_prompt.md # First session prompt
│   └── coding_prompt.md      # Continuation session prompt
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Generated Project Structure

When the agent runs, it creates a project with this structure:

```
generations/my_project/
├── app_spec.txt             # Your project specification
├── feature_list.json        # Test cases (source of truth)
├── init.sh                  # Environment setup script
├── claude-progress.txt      # Session progress notes
├── .claude_settings.json    # Security settings
└── [application files]      # Generated application code
```

**Key Point:** Each project has its own `app_spec.txt` in its directory!

## Customization

### Change the Application

#### Option 1: Use the Interactive Spec Builder (Recommended)

```bash
# Claude helps you create a comprehensive spec
python spec_builder.py

# Or integrated with the main agent
python autonomous_agent_demo.py --create-spec --project-dir ./my_app
```

#### Option 2: Manually Create the Spec

Create `app_spec.txt` in your project directory:

```bash
# Create project directory
mkdir -p generations/my_app

# Create or edit the specification
nano generations/my_app/app_spec.txt

# Or copy the example template
cp prompts/app_spec.txt generations/my_app/app_spec.txt
nano generations/my_app/app_spec.txt
```

### Adjust Feature Count

For faster demos, edit `prompts/initializer_prompt.md` to create fewer test cases (e.g., 20-30 for quick testing).

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

- **First session**: 5-10 minutes (generating 40-50 test cases)
- **Subsequent sessions**: 5-15 minutes each
- **Complete application**: Many hours across multiple sessions

**Tip**: Use `--max-iterations 3` for quick testing

## Interrupting and Resuming

You can interrupt the agent at any time with `Ctrl+C`. To resume:

```bash
# Run the same command again
python autonomous_agent_demo.py --project-dir ./my_project
```

### How Resume Works:

The agent automatically detects project state:

1. **No feature_list.json** → Runs initialization (first session)
2. **feature_list.json exists** → Resumes coding (continuation session)

When resuming, the agent:
- ✅ Reads `feature_list.json` to see completed tests
- ✅ Checks `claude-progress.txt` for session notes
- ✅ Reviews `git log` for recent changes
- ✅ Shows progress summary (X/Y tests passing)
- ✅ Continues from next incomplete feature

**Edge Case:** If initialization crashes before completing `feature_list.json`, the agent will detect incomplete work and try to complete it rather than starting over.

### State Persistence:

Your project state is saved in:
- `feature_list.json` - Test suite (source of truth)
- `claude-progress.txt` - Session notes
- `.git/` - Version history
- Application files - Generated code

## Full System Access (Normal Mode)

The autonomous agent runs as a **normal Python script with full system access** - NOT sandboxed.

### What This Means:
✅ **Full Capabilities:**
- ✅ Can start dev servers on any port (5173, 3000, 8000, etc.)
- ✅ Can use Puppeteer for browser automation
- ✅ Can execute bash commands
- ✅ Can read/write anywhere in project directory
- ✅ Full access to your system

### No Restrictions:
This is the standard way Python scripts run. No sandboxing, no limitations.

### How Testing Works:

The agent verifies features by:
1. ✅ Code review (checking implementation correctness)
2. ✅ TypeScript compilation (`npx tsc --noEmit`)
3. ✅ Build verification (`npm run build`)
4. ✅ Linting checks (`npm run lint`)
5. ✅ Browser automation (Puppeteer) - starts dev server and tests UI
6. ✅ Manual verification steps documented

See [NORMAL_MODE_GUIDE.md](./docs/NORMAL_MODE_GUIDE.md) for detailed information.

## Running the Generated Application

After the agent creates your application, you can test it locally outside the sandbox:

```bash
cd generations/my_project

# Run the setup script
./init.sh

# Or manually (typical for Node.js apps)
npm install
npm run dev
```

The application will be available at `http://localhost:5173` or `http://localhost:3000`.

**Note**: The agent runs the build step (`npm run build`) to generate the `dist/` folder, which can be deployed without a dev server.

## Troubleshooting

### Authentication Issues

**Using Claude Subscription (default):**
```bash
# 1. Get your OAuth token
claude setup-token

# 2. Set the environment variable
export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token-from-step-1'

# 3. Run the agent
python autonomous_agent_demo.py --project-dir ./my_app
```

**Using API Key:**
```bash
# Make sure API key is set
export ANTHROPIC_API_KEY='your-api-key-here'

# Use --auth-method api-key
python autonomous_agent_demo.py --project-dir ./my_app --auth-method api-key
```

### OAuth Token Not Set

If you see an error about `CLAUDE_CODE_OAUTH_TOKEN`:
```bash
# Run this command and copy the token
claude setup-token

# Then set it
export CLAUDE_CODE_OAUTH_TOKEN='paste-your-token-here'
```

### Testing Your Authentication

Run the authentication test to verify your token works:
```bash
python test_auth.py
```

This will:
1. ✅ Check if your token/key is set in `.env`
2. 🔌 Make a real API call to Claude
3. ✅ Verify authentication works
4. 📝 Show helpful error messages if something is wrong

**If you get "Invalid API key" error:**
- Your OAuth token might be expired (tokens last 1 year)
- Get a fresh token: `claude setup-token`
- Update your `.env` file with the new token

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

### Quick Test Run (Claude Subscription)

```bash
# Quick spec generation (type 'skip' when prompted)
python autonomous_agent_demo.py --create-spec --project-dir ./quick_demo

# Then run with limited iterations
python autonomous_agent_demo.py \
  --project-dir ./quick_demo \
  --max-iterations 2
```

### Using API Key

```bash
# Same demo but with API key authentication
python autonomous_agent_demo.py \
  --project-dir ./quick_demo \
  --max-iterations 3 \
  --auth-method api-key
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

## Roadmap

### Upcoming Features

- 🔗 **Linear Integration**: Sync feature progress with Linear issues and update task status automatically
- 🔗 **GitHub Projects Integration**: Track development progress in GitHub Projects boards
- Additional project management integrations planned

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
