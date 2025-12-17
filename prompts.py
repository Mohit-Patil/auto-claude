"""
Utilities for loading prompt files.
"""

from pathlib import Path


def load_prompt(filename: str) -> str:
    """
    Load a prompt file from the prompts directory.

    Args:
        filename: Name of the prompt file (e.g., 'initializer_prompt.md')

    Returns:
        Contents of the prompt file

    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompt_path = Path(__file__).parent / "prompts" / filename

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text()


def load_app_spec() -> str:
    """
    Load the application specification.

    Returns:
        Contents of app_spec.txt
    """
    return load_prompt("app_spec.txt")


def load_initializer_prompt() -> str:
    """
    Load the initializer agent prompt.

    Returns:
        Contents of initializer_prompt.md
    """
    return load_prompt("initializer_prompt.md")


def load_coding_prompt() -> str:
    """
    Load the coding agent prompt.

    Returns:
        Contents of coding_prompt.md
    """
    return load_prompt("coding_prompt.md")
