"""
Agent session management and execution logic.
"""

import asyncio
from pathlib import Path
from claude_agent_sdk import (
    ClaudeSDKClient,
    AssistantMessage,
    ToolUseBlock,
    ToolResultBlock,
    TextBlock,
    ResultMessage
)
from client import create_client
from progress import is_first_run, display_session_header
from prompts import load_initializer_prompt, load_coding_prompt


# Delay between sessions (in seconds)
AUTO_CONTINUE_DELAY_SECONDS = 3


async def run_agent_session(
    client: ClaudeSDKClient,
    prompt: str,
    iteration: int
) -> tuple[str, str]:
    """
    Run a single agent session.

    Args:
        client: The Claude SDK client
        prompt: The prompt to send to the agent
        iteration: Current iteration number

    Returns:
        Tuple of (status, response_text)
        status: "continue" or "error"
        response_text: The agent's final response
    """
    print(f"\n{'='*70}")
    print(f"Starting session {iteration}...")
    print(f"{'='*70}\n")

    # Send the prompt
    await client.query(prompt)

    # Track the response
    response_text = ""
    has_error = False

    # Process messages with timeout
    print("⏳ Waiting for agent response (timeout: 15 minutes)...\n")

    try:
        async def process_messages():
            nonlocal response_text, has_error

            async for message in client.receive_messages():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # Display agent's text responses
                            print(f"\n{block.text}\n")
                            response_text += block.text + "\n"

                        elif isinstance(block, ToolUseBlock):
                            # Display tool usage
                            tool_input_str = str(block.input)
                            if len(tool_input_str) > 200:
                                tool_input_str = tool_input_str[:200] + "..."

                            print(f"🔧 Using tool: {block.name}")
                            print(f"   Input: {tool_input_str}")

                elif isinstance(message, ToolResultBlock):
                    # Display tool results
                    if message.is_error:
                        print(f"   ❌ [Error]")
                        has_error = True
                    else:
                        print(f"   ✅ [Done]")

                elif isinstance(message, ResultMessage):
                    # Session completed
                    print(f"\n{'='*70}")
                    print(f"Session {iteration} completed")
                    print(f"Duration: {message.duration_ms / 1000:.2f}s")
                    print(f"Turns: {message.num_turns}")

                    if message.total_cost_usd:
                        print(f"Cost: ${message.total_cost_usd:.4f}")

                    print(f"{'='*70}\n")

                    if message.is_error:
                        has_error = True

                    # Break out of the message loop
                    break

        # 15-minute timeout for agent sessions (they can be long-running)
        await asyncio.wait_for(process_messages(), timeout=900.0)

    except asyncio.TimeoutError:
        print("\n⚠️  Timeout: Agent session exceeded 15 minutes")
        print("   This might indicate the agent is stuck or the task is too complex.")
        print("   The session will retry automatically.\n")
        has_error = True
    except Exception as e:
        print(f"\n⚠️  Error processing messages: {e}")
        has_error = True

    status = "error" if has_error else "continue"
    return status, response_text


async def run_autonomous_agent(
    project_dir: Path,
    model: str = "claude-sonnet-4-5-20250929",
    max_iterations: int | None = None,
    auth_method: str = "subscription"
):
    """
    Run the autonomous agent in a loop.

    The agent will:
    1. First session: Initialize the project with feature_list.json
    2. Subsequent sessions: Implement features incrementally

    Args:
        project_dir: Path to the project directory
        model: Claude model to use
        max_iterations: Optional maximum number of iterations (None for unlimited)
        auth_method: Authentication method - "subscription" or "api-key"
    """
    project_dir = Path(project_dir).absolute()
    iteration = 1
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 3

    print("\n" + "="*70)
    print("  AUTONOMOUS CODING AGENT")
    print("="*70)
    print(f"\nProject directory: {project_dir}")
    print(f"Model: {model}")

    if max_iterations:
        print(f"Max iterations: {max_iterations}")
    else:
        print("Max iterations: Unlimited")

    print("\n⚠️  This demo will take a long time to run!")
    print("   - First session: Several minutes (generating test cases)")
    print("   - Subsequent sessions: 5-15 minutes each")
    print("   - You can interrupt with Ctrl+C and resume later")

    while True:
        if max_iterations and iteration > max_iterations:
            print(f"\nReached maximum iterations ({max_iterations}). Stopping.")
            break

        # Display session header
        display_session_header(iteration, project_dir)

        # Determine which prompt to use
        is_first = is_first_run(project_dir)

        if is_first:
            print("📝 Loading initializer prompt...")
            prompt = load_initializer_prompt()
            print("   This session will create feature_list.json and set up the project.\n")
        else:
            print("📝 Loading coding prompt...")
            prompt = load_coding_prompt()
            print("   This session will continue implementing features.\n")

        # Create a fresh client for this session
        print("🔌 Connecting to Claude...")

        try:
            async with create_client(project_dir, model, auth_method) as client:
                # Run the session
                status, response = await run_agent_session(client, prompt, iteration)

                if status == "error":
                    consecutive_failures += 1
                    print(f"\n⚠️  Session ended with errors (consecutive failures: {consecutive_failures}/{MAX_CONSECUTIVE_FAILURES})")

                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        print(f"\n❌ Reached maximum consecutive failures ({MAX_CONSECUTIVE_FAILURES})")
                        print("   This usually means:")
                        print("   - The task is too complex or ambiguous")
                        print("   - There's a network connectivity issue")
                        print("   - The authentication token has expired")
                        print("\n   Please check the error messages above and try again.")
                        break
                    else:
                        print("   Retrying in next session...")
                else:
                    consecutive_failures = 0  # Reset on success
                    print("\n✅ Session completed successfully!")

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user!")
            print(f"\nTo resume, run the same command again:")
            print(f"  python autonomous_agent_demo.py --project-dir {project_dir}")
            break
        except Exception as e:
            consecutive_failures += 1
            print(f"\n❌ Error in session {iteration}: {str(e)}")
            print(f"   Consecutive failures: {consecutive_failures}/{MAX_CONSECUTIVE_FAILURES}")

            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print(f"\n❌ Too many consecutive failures. Stopping.")
                print("   Check your authentication and network connection.")
                break
            else:
                print("   Will retry in next session...")

        # Auto-continue delay
        if not max_iterations or iteration < max_iterations:
            print(f"\n⏸️  Waiting {AUTO_CONTINUE_DELAY_SECONDS} seconds before next session...")
            print("   (Press Ctrl+C to stop)\n")

            try:
                await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user!")
                print(f"\nTo resume, run the same command again:")
                print(f"  python autonomous_agent_demo.py --project-dir {project_dir}")
                break

        iteration += 1

    print("\n" + "="*70)
    print("  AUTONOMOUS AGENT STOPPED")
    print("="*70)
    print(f"\nTotal sessions completed: {iteration - 1}")
    print(f"Project directory: {project_dir}")

    if is_first_run(project_dir):
        print("\n⚠️  Project not fully initialized yet.")
        print("   Run again to continue setup.")
    else:
        print("\n📦 To run your generated application:")
        print(f"   cd {project_dir}")
        print("   ./init.sh")
        print("\n   (Or follow the README.md in the project directory)")

    print("\n" + "="*70 + "\n")
