#!/usr/bin/env python3
"""
Autonomous Coding Agent Demo

A minimal harness demonstrating long-running autonomous coding with the Claude Agent SDK.

This implements a two-agent pattern:
1. Initializer agent (first session): Sets up project, creates feature_list.json with 40-50 test cases
2. Coding agent (subsequent sessions): Implements features incrementally

Usage:
    # Using Claude Subscription (default)
    # 1. Get OAuth token: claude setup-token
    # 2. Set token: export CLAUDE_CODE_OAUTH_TOKEN='your-token'
    # 3. Run:
    python autonomous_agent_demo.py --project-dir ./my_project

    # Using API Key
    python autonomous_agent_demo.py --project-dir ./my_project --auth-method api-key

    # Other options
    python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 3
    python autonomous_agent_demo.py --project-dir ./my_project --model claude-opus-4-5-20250929

Authentication:
    --auth-method subscription (default): Use Claude subscription OAuth token
                                         Set CLAUDE_CODE_OAUTH_TOKEN environment variable
    --auth-method api-key: Use ANTHROPIC_API_KEY environment variable
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
  # Create app specification first (recommended for new projects)
  python autonomous_agent_demo.py --create-spec --project-dir ./my_app

  # Using Claude Subscription (default)
  python autonomous_agent_demo.py --project-dir ./my_app

  # Using API Key instead
  python autonomous_agent_demo.py --project-dir ./my_app --auth-method api-key

  # Limit iterations (useful for testing)
  python autonomous_agent_demo.py --project-dir ./my_app --max-iterations 3

  # Use a different model
  python autonomous_agent_demo.py --project-dir ./my_app --model claude-opus-4-5-20250929

Authentication Methods:
  subscription (default)  Use your Claude subscription OAuth token
                         1. Get token: claude setup-token
                         2. Set: export CLAUDE_CODE_OAUTH_TOKEN='your-token'
                         Token is valid for 1 year

  api-key                Use Anthropic API key
                         Set: export ANTHROPIC_API_KEY='your-key'
                         Get from: https://console.anthropic.com/

The agent will work in sessions:
  - Session 1: Initialize project, create 40-50 test cases (~5-10 minutes)
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

    parser.add_argument(
        "--auth-method",
        type=str,
        choices=["subscription", "api-key"],
        default="subscription",
        help="Authentication method (default: subscription)"
    )

    parser.add_argument(
        "--create-spec",
        action="store_true",
        help="Interactively create app_spec.txt before starting the agent"
    )

    parser.add_argument(
        "--spec-file",
        type=str,
        default="prompts/app_spec.txt",
        help="Path to app specification file (default: prompts/app_spec.txt)"
    )

    return parser.parse_args()


async def create_spec_interactive(project_dir: Path):
    """Create app specification interactively.

    Args:
        project_dir: The project directory where the spec will be saved
    """
    from spec_builder import build_app_spec

    print("\n" + "=" * 70)
    print("  CREATING APP SPECIFICATION")
    print("=" * 70)
    print()

    spec = await build_app_spec(interactive=True)

    # Save to project directory
    project_dir.mkdir(parents=True, exist_ok=True)
    spec_path = project_dir / "app_spec.txt"

    with open(spec_path, 'w') as f:
        f.write(spec)

    print("\n" + "=" * 70)
    print("✅ SPECIFICATION CREATED!")
    print("=" * 70)
    print(f"\nSaved to: {spec_path}")
    print(f"Project directory: {project_dir}")
    print("\nReview the spec:")
    print(f"  cat {spec_path}")
    print("\nReady to start building!")
    print("=" * 70)
    print()

    return str(spec_path)


def main():
    """Main entry point."""
    args = parse_args()

    # Normalize project path early
    project_dir = Path(args.project_dir)
    if not project_dir.is_absolute():
        generations_dir = Path(__file__).parent / "generations"
        generations_dir.mkdir(exist_ok=True)
        project_dir = generations_dir / project_dir.name

    # Create spec first if requested
    if args.create_spec:
        try:
            spec_file = asyncio.run(create_spec_interactive(project_dir))
            print("\nProceed to start the autonomous agent? (y/n)")
            response = input("> ").strip().lower()
            if response != 'y':
                print("👋 Goodbye! Run the agent when you're ready:")
                print(f"  python autonomous_agent_demo.py --project-dir {args.project_dir}")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\n\n⚠️  Spec creation cancelled")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error creating spec: {e}")
            sys.exit(1)

    # Validate authentication based on method
    if args.auth_method == "api-key":
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("❌ Error: ANTHROPIC_API_KEY environment variable is required when using --auth-method api-key")
            print("\nGet your API key from: https://console.anthropic.com/")
            print("\nThen set it:")
            print("  export ANTHROPIC_API_KEY='your-api-key-here'")
            print("\nOr use Claude Subscription (default):")
            print("  claude setup-token")
            print("  export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token-here'")
            print("  python autonomous_agent_demo.py --project-dir ./my_app")
            sys.exit(1)
    else:  # subscription
        oauth_token = os.getenv("CLAUDE_CODE_OAUTH_TOKEN")
        if not oauth_token:
            print("❌ Error: CLAUDE_CODE_OAUTH_TOKEN environment variable is required for subscription authentication")
            print("\nTo set up OAuth token:")
            print("  1. Run: claude setup-token")
            print("  2. Copy the OAuth token (valid for 1 year)")
            print("  3. Set environment variable:")
            print("     export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token-here'")
            print("\nOr use API Key authentication:")
            print("  python autonomous_agent_demo.py --project-dir ./my_app --auth-method api-key")
            sys.exit(1)

        print("🔐 Using Claude Subscription authentication (OAuth token)")
        print(f"   Token: {oauth_token[:20]}...{oauth_token[-10:] if len(oauth_token) > 30 else ''}")

    # Run the autonomous agent
    try:
        asyncio.run(run_autonomous_agent(
            project_dir=project_dir,
            model=args.model,
            max_iterations=args.max_iterations,
            auth_method=args.auth_method
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
