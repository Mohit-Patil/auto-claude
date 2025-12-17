"""
Security module for bash command validation.

Uses an allowlist approach - only explicitly permitted commands can run.
Implements defense-in-depth with additional validation for sensitive operations.
"""

import re
import shlex
from typing import Any, Dict
from claude_agent_sdk import HookContext

# Allowed bash commands (minimal set for development)
ALLOWED_COMMANDS = {
    # File inspection
    "ls", "cat", "head", "tail", "wc", "grep",
    # File operations
    "cp", "mkdir", "chmod",
    # Node.js development
    "npm", "node", "npx",
    # Version control
    "git",
    # Process management
    "ps", "lsof", "sleep", "pkill",
    # Setup script
    "init.sh",
}

# Processes that can be killed (development servers only)
ALLOWED_PKILL_TARGETS = {
    "node", "npm", "npx", "vite", "next", "react-scripts"
}


def extract_commands(bash_command: str) -> list[str]:
    """
    Extract command names from a bash command string.

    Handles complex shell syntax including:
    - Pipes (|)
    - Command chaining (&&, ||, ;)
    - Quotes and escapes

    Args:
        bash_command: The bash command to parse

    Returns:
        List of command names found in the bash command
    """
    commands = []

    # Split on common command separators
    for segment in re.split(r'[;&|]+', bash_command):
        segment = segment.strip()
        if not segment:
            continue

        try:
            # Parse the command with shlex to handle quotes properly
            tokens = shlex.split(segment)
            if tokens:
                # Skip common shell keywords and get the actual command
                cmd = tokens[0]
                # Handle redirects and other operators
                if cmd not in ('if', 'then', 'else', 'fi', 'for', 'while', 'do', 'done', '(', ')'):
                    commands.append(cmd)
        except ValueError:
            # If shlex fails (e.g., unclosed quotes), try simple split
            cmd = segment.split()[0] if segment.split() else ""
            if cmd:
                commands.append(cmd)

    return commands


def validate_pkill(command: str) -> tuple[bool, str]:
    """
    Validate pkill commands to ensure they only target development processes.

    Args:
        command: The bash command to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Extract the process name being killed
    try:
        tokens = shlex.split(command)
        if "pkill" not in tokens:
            return True, ""

        # Find the process name (usually the last argument)
        process_name = None
        for token in reversed(tokens):
            if not token.startswith('-'):
                process_name = token
                break

        if not process_name:
            return False, "pkill command missing process name"

        # Check if it's an allowed target
        if process_name not in ALLOWED_PKILL_TARGETS:
            return False, f"pkill target '{process_name}' not allowed. Only development processes can be killed: {', '.join(ALLOWED_PKILL_TARGETS)}"

        return True, ""
    except Exception as e:
        return False, f"Error parsing pkill command: {str(e)}"


def validate_chmod(command: str) -> tuple[bool, str]:
    """
    Validate chmod commands to only allow making files executable.

    Args:
        command: The bash command to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Only allow +x variants (making files executable)
    if "chmod" not in command:
        return True, ""

    # Check for allowed patterns like u+x, a+x, +x
    allowed_patterns = [r'\+x', r'[ugo]\+x', r'a\+x', r'755', r'777']

    if any(re.search(pattern, command) for pattern in allowed_patterns):
        return True, ""

    return False, "chmod only allowed for making files executable (+x)"


def validate_init_sh(command: str) -> tuple[bool, str]:
    """
    Validate init.sh execution to ensure proper path.

    Args:
        command: The bash command to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if "init.sh" not in command:
        return True, ""

    # Only allow ./init.sh or paths ending in /init.sh
    if command.strip() == "./init.sh" or command.endswith("/init.sh"):
        return True, ""

    return False, "init.sh must be executed as ./init.sh or with full path ending in /init.sh"


async def validate_bash_command(
    input_data: Dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> Dict[str, Any]:
    """
    Hook function to validate bash commands before execution.

    Implements defense-in-depth:
    1. Command must be in allowlist
    2. Additional validation for sensitive commands (pkill, chmod, init.sh)

    Args:
        input_data: Tool input data containing the bash command
        tool_use_id: Optional tool use identifier
        context: Hook context

    Returns:
        Hook response with permission decision
    """
    if input_data.get('tool_name') != 'Bash':
        return {}

    command = input_data.get('tool_input', {}).get('command', '')

    # Extract all commands from the bash command
    commands = extract_commands(command)

    # Check each command against allowlist
    for cmd in commands:
        # Handle script execution
        if cmd.startswith('./'):
            cmd = cmd[2:]

        if cmd not in ALLOWED_COMMANDS:
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': f"Command '{cmd}' is not allowed. Only these commands are permitted: {', '.join(sorted(ALLOWED_COMMANDS))}"
                }
            }

    # Additional validation for sensitive commands
    validators = [
        validate_pkill,
        validate_chmod,
        validate_init_sh
    ]

    for validator in validators:
        is_valid, error_msg = validator(command)
        if not is_valid:
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': error_msg
                }
            }

    # Command passed all checks
    return {}
