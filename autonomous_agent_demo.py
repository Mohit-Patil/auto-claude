#!/usr/bin/env python3
"""
Autonomous Coding Agent Demo

A minimal harness demonstrating long-running autonomous coding with the Claude Agent SDK.

This implements a two-agent pattern:
1. Initializer agent (first session): Sets up project, creates feature_list.json with 200+ test cases
2. Coding agent (subsequent sessions): Implements features incrementally

Usage:
    python autonomous_agent_demo.py --project-dir ./my_project
    python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 3
    python autonomous_agent_demo.py --project-dir ./my_project --model claude-opus-4-5-20250929

Environment:
    ANTHROPIC_API_KEY: Required. Get from https://console.anthropic.com/
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from agent import run_autonomous_agent

# Load environment variables from .env file if it exists
load_dotenv()


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run an autonomous coding agent to build applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python autonomous_agent_demo.py --project-dir ./my_app

  # Limit iterations (useful for testing)
  python autonomous_agent_demo.py --project-dir ./my_app --max-iterations 3

  # Use a different model
  python autonomous_agent_demo.py --project-dir ./my_app --model claude-opus-4-5-20250929

Environment Variables:
  ANTHROPIC_API_KEY    Your Anthropic API key (required)
                       Get from: https://console.anthropic.com/

The agent will work in sessions:
  - Session 1: Initialize project, create 200+ test cases (~10-20 minutes)
  - Session 2+: Implement features one by one (~5-15 minutes each)

You can stop with Ctrl+C and resume later.
        """
    )

    parser.add_argument(
        "--project-dir",
        type=str,
        default="./autonomous_demo_project",
        help="Directory for the project (default: ./autonomous_demo_project)"
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of agent iterations (default: unlimited)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="claude-sonnet-4-5-20250929",
        help="Claude model to use (default: claude-sonnet-4-5-20250929)"
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable is required")
        print("\nGet your API key from: https://console.anthropic.com/")
        print("\nThen set it:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Normalize project path
    project_dir = Path(args.project_dir)

    # If relative path, place it under generations/
    if not project_dir.is_absolute():
        generations_dir = Path(__file__).parent / "generations"
        generations_dir.mkdir(exist_ok=True)
        project_dir = generations_dir / project_dir.name

    # Run the autonomous agent
    try:
        asyncio.run(run_autonomous_agent(
            project_dir=project_dir,
            model=args.model,
            max_iterations=args.max_iterations
        ))
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
