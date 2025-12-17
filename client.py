"""
Claude SDK client configuration with security controls.
"""

import json
import os
from pathlib import Path
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from security import validate_bash_command


def create_client(
    project_dir: Path,
    model: str = "claude-sonnet-4-5-20250929"
) -> ClaudeSDKClient:
    """
    Create a Claude SDK client with security controls.

    Implements defense-in-depth security:
    1. Sandbox isolation - OS-level bash command separation
    2. Permission restrictions - File operations limited to project directory
    3. Command validation - Bash security hook validates commands against allowlist

    Args:
        project_dir: Path to the project directory
        model: Claude model to use

    Returns:
        Configured ClaudeSDKClient instance

    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    # Ensure project directory exists
    project_dir = Path(project_dir).absolute()
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create .claude_settings.json for security configuration
    settings_path = project_dir / ".claude_settings.json"
    settings = {
        "permissions": {
            "edit": {
                "allow": [str(project_dir) + "/**"],
                "deny": []
            }
        },
        "sandbox": {
            "enabled": True
        }
    }

    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)

    # Configure agent options
    options = ClaudeAgentOptions(
        # Available tools for development
        allowed_tools=[
            "Read",      # Read files
            "Write",     # Create new files
            "Edit",      # Edit existing files
            "Glob",      # Find files by pattern
            "Grep",      # Search file contents
            "Bash",      # Run bash commands
        ],

        # Auto-approve file edits within the project directory
        permission_mode="acceptEdits",

        # Set working directory
        cwd=str(project_dir),

        # Load project settings
        settings=str(settings_path),
        setting_sources=["project"],  # Only load project settings (not user or local)

        # Maximum conversation turns (within a single session)
        # Note: This is different from max_iterations at the application level
        # - max_turns: Limits conversation turns in one agent session
        # - max_iterations: Limits number of sessions to run
        max_turns=1000,

        # Model selection
        model=model,

        # System prompt - position Claude as a full-stack developer
        system_prompt="""You are an expert full-stack developer working on an autonomous coding project.

You have access to file operations (Read, Write, Edit, Glob, Grep) and bash commands for development tasks.

Your work is automatically saved and tracked across sessions. Focus on:
- Writing clean, maintainable, production-quality code
- Following best practices and design patterns
- Comprehensive testing and error handling
- Clear documentation and comments
- Incremental progress with frequent commits

You are working within a sandboxed environment with security restrictions:
- File operations are restricted to the project directory
- Only approved bash commands can execute
- All changes are version controlled with git

Work methodically, test thoroughly, and document your progress.""",

        # Security hooks
        hooks={
            'PreToolUse': [
                {
                    'matcher': 'Bash',
                    'hooks': [validate_bash_command]
                }
            ]
        },

        # Include partial messages for progress tracking
        include_partial_messages=True
    )

    return ClaudeSDKClient(options)
