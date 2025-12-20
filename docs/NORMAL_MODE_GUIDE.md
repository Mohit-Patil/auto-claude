# Running Autonomous Agent in Normal Mode (Full System Access)

## ✅ You ARE Already Running in Normal Mode!

The autonomous agent runs as a **normal Python script on your machine** with full system access. It is NOT sandboxed.

### What This Means:

✅ **Full Access:**
- Can bind to any port (3000, 5173, 8000, etc.)
- Can start dev servers with `npm run dev`
- Can use Puppeteer for browser automation
- Can run any command (with security allowlist)
- Can read/write anywhere in project directory
- Can execute bash commands

❌ **No Sandboxing:**
- This is the standard way Python scripts run on your machine
- Same as running any terminal command

## Running the Autonomous Agent

### 1. Basic Usage (Recommended)

```bash
# Resume or continue the project
python autonomous_agent_demo.py --project-dir ./habit-tracker
```

The agent will:
- ✅ Check if `feature_list.json` exists
- ✅ If yes: Continue from where it left off (coding session)
- ✅ If no: Start fresh (initialization session)

### 2. Using Haiku (Cheaper)

```bash
# Use Haiku for faster, cheaper development
python autonomous_agent_demo.py \
  --project-dir ./habit-tracker \
  --model claude-3-5-haiku-20241022
```

### 3. With Limited Iterations (Testing)

```bash
# Run just 1 more session for testing
python autonomous_agent_demo.py \
  --project-dir ./habit-tracker \
  --max-iterations 1
```

### 4. Clean Start

```bash
# Delete everything and start fresh
rm -rf generations/habit-tracker

# Start initialization
python autonomous_agent_demo.py \
  --project-dir ./habit-tracker \
  --model claude-3-5-haiku-20241022
```

## How Sessions Work

### Session 1: Initialization
- Reads `app_spec.txt`
- Creates `feature_list.json` with 40-50 test cases
- Sets up project structure
- Creates `init.sh` setup script
- Initializes git repository

### Sessions 2+: Coding
- Reads `feature_list.json` to see progress
- Implements next incomplete feature
- Verifies code compiles and builds
- Updates `feature_list.json` when feature is complete
- Commits changes to git
- Auto-continues after 3 second delay

## What the Agent Can Do

### Full System Access:
```bash
# Start dev servers
npm run dev

# Run npm commands
npm install
npm run build
npm run lint

# Check files
ls -la
cat file.txt
grep "pattern" file.txt

# Git operations
git add .
git commit -m "message"
git log --oneline

# And more...
```

### Browser Automation Ready:
The agent can use Puppeteer to:
- Start a dev server
- Open a browser
- Click buttons, fill forms
- Take screenshots
- Verify UI functionality
- Automate complex workflows

## Resuming After Interruption

You can interrupt the agent at any time with `Ctrl+C`. To resume:

```bash
# Just run the same command again
python autonomous_agent_demo.py --project-dir ./habit-tracker
```

The agent will:
1. Check `feature_list.json` - See what's done
2. Read `claude-progress.txt` - Get context
3. Check `git log` - See recent changes
4. Continue from next incomplete feature

## Testing Your Generated App

After the agent builds the app, test it locally:

```bash
# Go to project directory
cd generations/habit-tracker

# Install dependencies (if needed)
npm install

# Start development server
npm run dev

# Open http://localhost:5173 in your browser
# Test the app manually
```

## Monitoring Agent Progress

### View Progress While Running:
```bash
# In another terminal, monitor the project
cd generations/habit-tracker

# See how many tests pass
jq '[.[] | select(.passes == true)] | length' feature_list.json

# See git commits
git log --oneline -10

# View progress notes
tail -50 claude-progress.txt
```

### Full Test Status:
```bash
# Count passing and failing tests
jq 'length as $total | [.[] | select(.passes == true)] | length as $pass | {total: $total, passing: $pass, percentage: ($pass/$total*100 | round)}' feature_list.json
```

## Environment

### Required:
- Python 3.10+ (you have 3.13 ✅)
- Node.js/npm (for building the React app)
- Claude subscription or API key

### Optional:
- Puppeteer (for browser automation - installed via npm)
- Git (for version control - usually pre-installed)

## Performance Tips

### Faster Development:
```bash
# Use Haiku model (3x faster, 10x cheaper than Sonnet)
python autonomous_agent_demo.py \
  --project-dir ./habit-tracker \
  --model claude-3-5-haiku-20241022
```

### Hybrid Approach:
```bash
# Phase 1: Quick development with Haiku
python autonomous_agent_demo.py \
  --project-dir ./habit-tracker \
  --model claude-3-5-haiku-20241022 \
  --max-iterations 10

# Phase 2: Polish with Sonnet if needed
python autonomous_agent_demo.py \
  --project-dir ./habit-tracker \
  --model claude-sonnet-4-5-20250929
```

## Troubleshooting

### "Model not found" Error
```
API Error: 404 {"error": "model: claude-xxx"}
```
**Solution**: Use correct model name:
- ✅ `claude-3-5-haiku-20241022` (Haiku 3.5)
- ✅ `claude-sonnet-4-5-20250929` (Sonnet 4.5)
- ✅ `claude-opus-4-5-20251101` (Opus 4.5)

### "Authentication Failed"
**Solution**: Set your OAuth token or API key:
```bash
# Using subscription (recommended)
export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'

# Or using API key
export ANTHROPIC_API_KEY='your-key-here'
python autonomous_agent_demo.py --project-dir ./habit-tracker --auth-method api-key
```

### Agent Seems Stuck
**Solution**: You have timeouts in place:
- 15-minute timeout per session
- 3 consecutive failure limit
- Agent will auto-stop if stuck

Check the output - it will tell you what's happening.

## Summary

✅ **You are running in NORMAL mode with full system access**
✅ **No sandboxing restrictions**
✅ **Agent can do anything a human developer can do**
✅ **All 40-50 test cases will work properly**
✅ **Browser automation is fully supported**

Just run:
```bash
python autonomous_agent_demo.py --project-dir ./habit-tracker
```

And watch your app build itself! 🚀
