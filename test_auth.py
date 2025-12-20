#!/usr/bin/env python3
"""
Quick test to verify authentication setup.
Run this to check if your authentication is configured correctly.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


async def test_authentication_real():
    """Test authentication by making a real API call."""
    from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

    oauth_token = os.getenv("CLAUDE_CODE_OAUTH_TOKEN")
    api_key = os.getenv("ANTHROPIC_API_KEY")

    print("=" * 70)
    print("  AUTHENTICATION TEST - LIVE API VERIFICATION")
    print("=" * 70)
    print()

    # Step 1: Check environment variables
    print("Step 1: Checking environment variables...")
    print()

    auth_method = None
    if oauth_token:
        print("✅ CLAUDE_CODE_OAUTH_TOKEN is set")
        print(f"   Token: {oauth_token[:20]}...{oauth_token[-10:] if len(oauth_token) > 30 else ''}")
        auth_method = "subscription"
    else:
        print("❌ CLAUDE_CODE_OAUTH_TOKEN is not set")

    print()

    if api_key:
        print("✅ ANTHROPIC_API_KEY is set")
        print(f"   Key: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else ''}")
        if not auth_method:
            auth_method = "api-key"
    else:
        print("❌ ANTHROPIC_API_KEY is not set")

    print()
    print("=" * 70)

    if not auth_method:
        print("\n❌ NO AUTHENTICATION METHOD AVAILABLE")
        print("\nPlease set up authentication:")
        print("\nOption 1 (Recommended): OAuth Token")
        print("  1. Run: claude setup-token")
        print("  2. Copy the token and add to .env file:")
        print("     CLAUDE_CODE_OAUTH_TOKEN=your-token-here")
        print("\nOption 2: API Key")
        print("  1. Get from: https://console.anthropic.com/")
        print("  2. Add to .env file:")
        print("     ANTHROPIC_API_KEY=your-key-here")
        print("\n" + "=" * 70)
        return

    # Step 2: Test with real API call
    print(f"\nStep 2: Testing {auth_method} authentication with Claude API...")
    print("         (This will make a real API call)")
    print()

    try:
        # Create a minimal options setup
        options = ClaudeAgentOptions(
            allowed_tools=["Read"],  # Minimal tool for testing
            max_turns=1,
            model="claude-sonnet-4-5-20250929"
        )

        print("🔌 Connecting to Claude...")

        async with ClaudeSDKClient(options) as client:
            print("✅ Connection established!")
            print()
            print("📤 Sending test query: 'Say hello in exactly 3 words'")

            # Send a simple test query
            await client.query("Say hello in exactly 3 words")

            # Receive response
            response_received = False
            async for message in client.receive_response():
                from claude_agent_sdk import AssistantMessage, TextBlock, ResultMessage

                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"📥 Received response: '{block.text}'")
                            response_received = True
                elif isinstance(message, ResultMessage):
                    if message.is_error:
                        print(f"❌ Error in response: {message}")
                        return
                    break

            if response_received:
                print()
                print("=" * 70)
                print("✅ SUCCESS! Authentication is working perfectly!")
                print("=" * 70)
                print()
                print(f"Authentication method: {auth_method}")
                if auth_method == "subscription":
                    print("Using: Claude Subscription (OAuth Token)")
                else:
                    print("Using: Anthropic API Key")
                print()
                print("You're ready to run the autonomous agent:")
                if auth_method == "subscription":
                    print("  python autonomous_agent_demo.py --project-dir ./my_app")
                else:
                    print("  python autonomous_agent_demo.py --project-dir ./my_app --auth-method api-key")
                print()
                print("=" * 70)
            else:
                print("\n⚠️  No response received from API")

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ AUTHENTICATION FAILED!")
        print("=" * 70)
        print()
        print(f"Error: {str(e)}")
        print()

        if "api key" in str(e).lower() or "authentication" in str(e).lower():
            print("Possible issues:")
            print("  1. Token/key might be expired or invalid")
            print("  2. Token/key might be incorrectly formatted in .env file")
            print("  3. Network connectivity issues")
            print()
            if auth_method == "subscription":
                print("To fix OAuth token:")
                print("  1. Get a fresh token: claude setup-token")
                print("  2. Update .env file with new token")
                print()
            else:
                print("To fix API key:")
                print("  1. Get a fresh key from: https://console.anthropic.com/")
                print("  2. Update .env file with new key")
                print()
        else:
            print("Unexpected error occurred. Full error details:")
            import traceback
            traceback.print_exc()

        print("=" * 70)


def main():
    """Main entry point."""
    try:
        asyncio.run(test_authentication_real())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
