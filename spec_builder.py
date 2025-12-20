#!/usr/bin/env python3
"""
Interactive App Specification Builder

Helps you create a comprehensive app_spec.txt using Claude before starting
the autonomous development process.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

# Load environment variables
load_dotenv()


SPEC_BUILDER_PROMPT = """You are an expert product manager and software architect helping create a comprehensive, step-by-step application specification.

The user will describe what they want to build. Your job is to help them create a DETAILED, STEP-BY-STEP app specification in XML format that will guide an autonomous coding agent.

Ask clarifying questions to understand:
- What problem does this solve?
- Who will use it?
- What are the must-have features vs nice-to-have?
- Any specific technologies they want to use?
- Any design preferences (colors, fonts, layout)?
- How should data be stored?

Then create a comprehensive specification following this EXACT XML format (write the XML directly, NOT in a code block):

<project_specification>
  <project_name>[Name of the project]</project_name>

  <overview>
  [2-3 sentence executive summary describing what this application does and its primary purpose]
  </overview>

  <technology_stack>
    <frontend>
      <framework>[e.g., React 18 with TypeScript]</framework>
      <styling>[e.g., Tailwind CSS]</styling>
      <state_management>[e.g., React Context, Zustand]</state_management>
      <build_tool>[e.g., Vite]</build_tool>
      <router>[e.g., React Router]</router>
    </frontend>

    <backend>
      <storage>[e.g., LocalStorage, IndexedDB, or backend API]</storage>
      <database>[if applicable]</database>
    </backend>

    <development_tools>
      <linter>ESLint + Prettier</linter>
      <typescript>TypeScript</typescript>
    </development_tools>
  </technology_stack>


  <core_features>
    <feature_category_1>
      <name>[Feature Category Name]</name>
      <details>
        - [Specific implementation detail with technical specifics]
        - [How users interact with this feature]
        - [Libraries or patterns to use]
        - [Edge cases to handle]
        - [5-15 detailed points per category]
      </details>
    </feature_category_1>

    <feature_category_2>
      <name>[Another Feature]</name>
      <details>
        - [Implementation detail]
        - [User interaction]
        - [Technical approach]
      </details>
    </feature_category_2>

    <!-- Continue for all major features (5-10 categories) -->
  </core_features>

  <database_schema>
    <tables>
      <table_name>
        - field1: type (constraints)
        - field2: type (constraints)
        - field3: JSON object with {structure}
        - relationships: [foreign keys, references]
      </table_name>

      <!-- Add all necessary tables -->
    </tables>
  </database_schema>

  <ui_layout>
    <structure>
    [Describe the visual layout]
    - Overall structure (e.g., "Two-column layout: sidebar + main content")
    - Navigation placement and structure
    - Component hierarchy
    - Responsive behavior at different breakpoints (mobile, tablet, desktop)
    </structure>
  </ui_layout>

  <design_system>
    <colors>
      <primary>#[hex code]</primary>
      <secondary>#[hex code]</secondary>
      <background>#[hex code]</background>
      <text>#[hex code]</text>
      <accent>#[hex code]</accent>
    </colors>

    <typography>
      <headings>[font family, sizes]</headings>
      <body>[font family, size, line-height]</body>
      <code>[monospace font if applicable]</code>
    </typography>

    <components>
      <buttons>[styling details, hover states, sizes]</buttons>
      <cards>[padding, shadows, borders]</cards>
      <forms>[input styles, validation styling]</forms>
      <modals>[backdrop, positioning, animations]</modals>
    </components>

    <animations>
      <transitions>[duration, easing]</transitions>
      <hover_effects>[specifications]</hover_effects>
    </animations>
  </design_system>

  <implementation_steps>
    <step number="1">
      <title>Project Setup and Configuration</title>
      <tasks>
        - Initialize [framework] with [build tool]
        - Install dependencies: [list exact package names]
        - Configure ESLint with [specific rules]
        - Set up Prettier with [formatting options]
        - Create folder structure: src/, components/, utils/, etc.
        - Configure TypeScript with strict mode
      </tasks>
    </step>

    <step number="2">
      <title>[Next Phase Name]</title>
      <tasks>
        - [Specific task 1]
        - [Specific task 2]
        - [Testing for this phase]
      </tasks>
    </step>

    <!-- Continue with 8-12 numbered steps -->

    <step number="9">
      <title>Final Polish and Deployment</title>
      <tasks>
        - Performance optimization
        - Accessibility audit (WCAG 2.1 AA compliance)
        - Cross-browser testing
        - Build production bundle
        - Create deployment documentation
      </tasks>
    </step>
  </implementation_steps>

  <success_criteria>
    <functionality>
      - [Measurable outcome 1]
      - [Measurable outcome 2]
      - [All core features working end-to-end]
    </functionality>

    <performance>
      - [Performance metric with target, e.g., "Initial load under 2 seconds"]
      - [Performance metric 2]
    </performance>

    <user_experience>
      - [UX metric 1]
      - [Accessibility requirements met]
      - [Responsive across devices]
    </user_experience>

    <code_quality>
      - [No ESLint errors]
      - [TypeScript strict mode with no errors]
      - [Test coverage above X%]
    </code_quality>
  </success_criteria>
</project_specification>

CRITICAL INSTRUCTIONS:
- Generate VALID XML with proper opening and closing tags
- Be EXTREMELY specific (exact library versions, hex codes, port numbers)
- Each feature category should have 5-15 detailed implementation points
- Include exact technical specifications everywhere
- DO NOT wrap the XML in a code block - write the XML directly as the response
- The entire response should be valid XML that can be saved to a .txt file

Start by asking the user what they want to build, then gather requirements through conversation.
When you have enough information, generate the complete XML specification following the format above."""


async def build_app_spec(interactive: bool = True) -> str:
    """
    Interactive app specification builder.

    Args:
        interactive: If True, allows back-and-forth with Claude to refine the spec

    Returns:
        The final app specification text
    """
    print("=" * 70)
    print("  APP SPECIFICATION BUILDER")
    print("=" * 70)
    print()
    print("This tool will help you create a comprehensive app specification")
    print("that Claude can use to build your application autonomously.")
    print()
    print("=" * 70)
    print()

    # Get initial description
    print("What would you like to build?")
    print("(Describe your app idea in as much or as little detail as you want)")
    print()
    user_idea = input("Your idea: ").strip()

    if not user_idea:
        print("❌ No input provided. Exiting.")
        sys.exit(1)

    print()
    print("=" * 70)
    print("🤖 Claude is analyzing your idea and will ask clarifying questions...")
    print("=" * 70)
    print()

    # Create Claude client
    options = ClaudeAgentOptions(
        allowed_tools=[],  # No tools needed for this conversation
        max_turns=20,  # Allow multiple back-and-forth exchanges
        model="claude-sonnet-4-5-20250929",
        system_prompt=SPEC_BUILDER_PROMPT
    )

    conversation_history = []
    final_spec = None

    async with ClaudeSDKClient(options) as client:
        # Start conversation with user's idea
        initial_prompt = f"The user wants to build: {user_idea}\n\nPlease help them create a comprehensive app specification. Start by asking 3-5 key clarifying questions about features, tech stack, and design."

        print("💬 Starting conversation with Claude...\n")
        await client.query(initial_prompt)

        turn = 1
        max_turns = 6  # Limit to 6 turns to prevent infinite loops

        while turn <= max_turns:
            print(f"\n{'='*70}")
            print(f"  Turn {turn}/{max_turns}")
            print(f"{'='*70}\n")

            # Get Claude's response with timeout
            claude_response = ""
            print("⏳ Waiting for Claude's response (timeout: 120 seconds)...")
            print("   💡 Tip: If taking too long, press Ctrl+C and restart with 'skip'\n")

            try:
                async def get_response():
                    response = ""
                    async for message in client.receive_response():
                        if isinstance(message, AssistantMessage):
                            for block in message.content:
                                if isinstance(block, TextBlock):
                                    response += block.text
                    return response

                claude_response = await asyncio.wait_for(
                    get_response(),
                    timeout=120.0  # 120 second timeout
                )
            except asyncio.TimeoutError:
                print("\n⚠️  Timeout: Claude didn't respond within 120 seconds")
                print("🔄 Generating spec with information collected so far...\n")

                # Trigger immediate spec generation
                await client.query("Please generate the COMPLETE, FINAL app specification now in valid XML format based on our discussion. Include ALL sections: project_name, overview, technology_stack, core_features (with 5-10 feature categories), database_schema, ui_layout, design_system, implementation_steps (8-12 steps), and success_criteria. Write the XML directly without wrapping it in code blocks.")

                # Get the final spec
                final_spec = ""
                try:
                    async for message in client.receive_response():
                        if isinstance(message, AssistantMessage):
                            for block in message.content:
                                if isinstance(block, TextBlock):
                                    final_spec += block.text
                                    print(".", end="", flush=True)
                except Exception as e:
                    print(f"\n⚠️  Error getting final spec: {e}")

                print("\n")
                if final_spec:
                    break
                else:
                    print("❌ Could not generate spec. Please try again.")
                    sys.exit(1)
            except Exception as e:
                print(f"\n⚠️  Error receiving response: {e}")
                print("Continuing with what we have...\n")
                break

            if not claude_response.strip():
                print("\n⚠️  Empty response from Claude. Generating spec with current info...")
                break

            print(f"\nClaude:\n{claude_response}")
            print()

            # Check if Claude has generated a final spec (look for XML format)
            if "<project_specification>" in claude_response or "<?xml" in claude_response:
                # Don't extract code blocks - use the full response
                # Claude's response IS the spec in XML format
                final_spec = claude_response.strip()

                if not interactive:
                    break

                print("\n" + "=" * 70)
                print("📄 DRAFT SPECIFICATION:")
                print("=" * 70)
                print()
                print(final_spec if final_spec else claude_response)
                print()
                print("=" * 70)
                print()
                print("Options:")
                print("  [a] Accept this specification")
                print("  [r] Request revisions")
                print("  [q] Quit without saving")
                print()
                choice = input("Your choice (a/r/q): ").strip().lower()

                if choice == 'a':
                    break
                elif choice == 'q':
                    print("\n❌ Cancelled. No specification saved.")
                    sys.exit(0)
                elif choice == 'r':
                    print("\nWhat changes would you like?")
                    revision = input("Your feedback: ").strip()
                    await client.query(f"Please revise the specification based on this feedback: {revision}")
                    turn += 1
                    continue
            else:
                # Claude is asking questions, get user response
                if not interactive:
                    # In non-interactive mode, just accept what we have
                    break

                print("\n" + "="*70)
                print("OPTIONS:")
                print("  - Type your answer to Claude's questions")
                print("  - Type 'done' to generate the spec now")
                print("  - Type 'skip' to skip questions and generate spec immediately")
                print("="*70)
                print("\nYour response:")
                user_response = input("> ").strip()

                if not user_response:
                    print("\n⚠️  Empty response. Please provide an answer or type 'done'.")
                    continue

                if user_response.lower() in ['done', 'skip']:
                    print("\n" + "="*70)
                    print("🔄 GENERATING FINAL SPECIFICATION...")
                    print("="*70)
                    print("\n⏳ This may take 30-60 seconds...\n")

                    await client.query("I have all the information I need. Please generate the COMPLETE, FINAL app specification now in valid XML format. Include ALL sections: project_name, overview, technology_stack, core_features (with 5-10 feature categories), database_schema, ui_layout, design_system, implementation_steps (8-12 steps), and success_criteria. Write the XML directly without wrapping it in code blocks.")

                    # Get the final spec with timeout
                    final_spec = ""
                    try:
                        async def get_final_spec():
                            spec = ""
                            async for message in client.receive_response():
                                if isinstance(message, AssistantMessage):
                                    for block in message.content:
                                        if isinstance(block, TextBlock):
                                            spec += block.text
                                            print(".", end="", flush=True)  # Progress indicator
                            return spec

                        final_spec = await asyncio.wait_for(
                            get_final_spec(),
                            timeout=180.0  # 3 minute timeout for spec generation
                        )
                    except asyncio.TimeoutError:
                        print(f"\n⚠️  Timeout: Spec generation took longer than 3 minutes")
                        if final_spec:
                            print("Using partial spec generated so far...")
                        else:
                            print("❌ No spec generated. Please try again with simpler requirements.")
                            sys.exit(1)
                    except Exception as e:
                        print(f"\n⚠️  Error getting final spec: {e}")
                        if final_spec:
                            print("Using partial spec generated so far...")
                        else:
                            raise

                    print("\n")  # New line after progress dots
                    final_spec = final_spec.strip()

                    if not final_spec:
                        print("\n❌ No spec generated. Please try again.")
                        sys.exit(1)

                    break  # Exit the loop after getting the spec

                # User provided an answer, continue conversation
                print(f"\n📤 Sending your response to Claude...")
                await client.query(user_response)
                turn += 1

            # Check if we hit max turns
            if turn > max_turns:
                print("\n" + "="*70)
                print("⚠️  Reached maximum conversation turns")
                print("="*70)
                print("\nGenerating spec with current information...")

                await client.query("Please generate the complete app specification now based on what we've discussed so far.")

                try:
                    async def get_max_turns_spec():
                        spec = ""
                        async for message in client.receive_response():
                            if isinstance(message, AssistantMessage):
                                for block in message.content:
                                    if isinstance(block, TextBlock):
                                        spec += block.text
                                        print(".", end="", flush=True)
                        return spec

                    final_spec = await asyncio.wait_for(
                        get_max_turns_spec(),
                        timeout=180.0  # 3 minute timeout
                    )
                    print("\n")
                except asyncio.TimeoutError:
                    print("\n⚠️  Timeout generating spec after max turns")
                    if final_spec:
                        print("Using partial spec...")
                except Exception as e:
                    print(f"\n⚠️  Error: {e}")

                break

    if not final_spec:
        final_spec = claude_response

    return final_spec


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Build an app specification with Claude's help")
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Generate spec without back-and-forth (faster but less refined)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="prompts/app_spec.txt",
        help="Output file path (default: prompts/app_spec.txt)"
    )

    args = parser.parse_args()

    try:
        spec = await build_app_spec(interactive=not args.non_interactive)

        # Save to file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(spec)

        print()
        print("=" * 70)
        print("✅ SPECIFICATION SAVED!")
        print("=" * 70)
        print()
        print(f"Location: {output_path}")
        print()
        print("Next steps:")
        print("  1. Review the spec: cat", str(output_path))
        print("  2. Edit if needed: nano", str(output_path))
        print("  3. Start the agent: python autonomous_agent_demo.py --project-dir ./my_app")
        print()
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
