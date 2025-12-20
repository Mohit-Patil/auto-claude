"""
Progress tracking utilities for the autonomous agent.
"""

import json
from pathlib import Path
from typing import Dict, List


def get_feature_list_path(project_dir: Path) -> Path:
    """Get the path to feature_list.json."""
    return project_dir / "feature_list.json"


def get_progress_file_path(project_dir: Path) -> Path:
    """Get the path to claude-progress.txt."""
    return project_dir / "claude-progress.txt"


def is_first_run(project_dir: Path) -> bool:
    """
    Check if this is the first run (no feature_list.json exists).

    Args:
        project_dir: Path to the project directory

    Returns:
        True if this is the first run, False otherwise
    """
    return not get_feature_list_path(project_dir).exists()


def load_feature_list(project_dir: Path) -> List[Dict]:
    """
    Load the feature list from feature_list.json.

    Args:
        project_dir: Path to the project directory

    Returns:
        List of feature dictionaries

    Raises:
        FileNotFoundError: If feature_list.json doesn't exist
    """
    feature_list_path = get_feature_list_path(project_dir)

    if not feature_list_path.exists():
        raise FileNotFoundError(f"Feature list not found: {feature_list_path}")

    with open(feature_list_path, 'r') as f:
        return json.load(f)


def get_progress_summary(project_dir: Path) -> str:
    """
    Generate a progress summary from the feature list.

    Args:
        project_dir: Path to the project directory

    Returns:
        A formatted progress summary string
    """
    try:
        features = load_feature_list(project_dir)
        total = len(features)
        completed = sum(1 for f in features if f.get('passes', False))
        remaining = total - completed

        percentage = (completed / total * 100) if total > 0 else 0

        summary = f"""
╔════════════════════════════════════════════════════════════════╗
║                     PROGRESS SUMMARY                           ║
╚════════════════════════════════════════════════════════════════╝

  Total Features:     {total}
  Completed:          {completed}
  Remaining:          {remaining}
  Progress:           {percentage:.1f}%

  Next Priority Features:
"""

        # Show next 5 incomplete features
        incomplete = [f for f in features if not f.get('passes', False)]
        for i, feature in enumerate(incomplete[:5], 1):
            summary += f"    {i}. {feature.get('feature', 'Unknown feature')}\n"

        if len(incomplete) > 5:
            summary += f"    ... and {len(incomplete) - 5} more\n"

        return summary

    except FileNotFoundError:
        return "No feature list found yet. This will be created in the first session."
    except Exception as e:
        return f"Error generating progress summary: {str(e)}"


def display_session_header(iteration: int, project_dir: Path):
    """
    Display a header for the current session.

    Args:
        iteration: Current iteration number
        project_dir: Path to the project directory
    """
    is_first = is_first_run(project_dir)

    print("\n" + "=" * 70)
    if is_first:
        print(f"  SESSION {iteration}: INITIALIZATION")
        print("  This session will set up the project foundation")
    else:
        print(f"  SESSION {iteration}: CODING")
        print("  Continuing development work")
    print("=" * 70)

    if not is_first:
        print(get_progress_summary(project_dir))

    print("=" * 70 + "\n")
