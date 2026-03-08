"""
SudoMode Hackathon Demo: Autonomous Refund Agent
=================================================

LangChain-powered retail agent that demonstrates SudoMode's
zero-trust governance in action.

THE DEMO SCENARIO:
  1. User asks for a $500 refund
  2. Agent attempts to call issue_refund(amount=500)
  3. SudoMode Gateway intercepts and checks the policy (limit: $50)
  4. Gateway returns ACCESS DENIED: POLICY VIOLATION
  5. Threat Analyzer runs AI-powered risk analysis via Bedrock

Prerequisites:
--------------
1. Install dependencies:
     cd sdk
     pip install -r requirements.txt

2. AWS credentials configured for Bedrock access (optional for threat analysis)

Usage:
------
    cd sdk
    python examples/retail_agent.py

NOTE: This agent does NOT require the SudoMode server to be running.
      It uses the gateway module directly for the hackathon demo.
"""

import sys
import os
import re
from pathlib import Path

# ── Path setup ───────────────────────────────────────────────
# Add sdk/ to path for sudomode imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Add server/ to path for gateway and threat analyzer imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server"))

from app.core.gateway import evaluate_call
from app.services.threat_analyzer import analyze_threat

# ── LangChain + Bedrock imports ──────────────────────────────
try:
    from langchain_aws import ChatBedrock
    from langchain_core.tools import tool
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️  langchain-aws not installed. Running in standalone mode.")
    print("   Install with: pip install langchain-aws langchain-core")


# ============================================================================
# THE TOOL: issue_refund — protected by SudoMode Gateway
# ============================================================================

if LANGCHAIN_AVAILABLE:
    @tool
    def issue_refund(amount: float, order_id: str) -> str:
        """Issue a refund for a customer order.

        Args:
            amount: The refund amount in dollars.
            order_id: The order ID to refund.
        """
        print(f"\n🔄 Agent is attempting: issue_refund(amount=${amount}, order_id={order_id})")

        # ── CRITICAL: Route through SudoMode Gateway FIRST ──
        verdict = evaluate_call("issue_refund", {"amount": amount, "order_id": order_id})

        if verdict != "ALLOW":
            # ⛔ BLOCKED — trigger threat analysis
            print(f"\n⛔ {verdict}")
            print("🔍 Triggering automated threat analysis...")

            analysis = analyze_threat({
                "tool": "issue_refund",
                "amount": amount,
                "limit": 50,
                "order_id": order_id,
            })

            return (
                f"ACCESS DENIED: POLICY VIOLATION. "
                f"Refund of ${amount} for order {order_id} was BLOCKED. "
                f"Policy limit is $50. "
                f"Threat Analysis: {analysis}"
            )

        # ✅ ALLOWED — proceed with the refund
        print(f"\n✅ Refund of ${amount} for order {order_id} processed successfully!")
        return f"SUCCESS: Refund of ${amount} issued for order {order_id}."


# ============================================================================
# STANDALONE FALLBACK (when langchain-aws is not installed)
# ============================================================================

def issue_refund_standalone(amount: float, order_id: str) -> str:
    """Standalone version of the refund tool (no LangChain required)."""
    print(f"\n🔄 Agent is attempting: issue_refund(amount=${amount}, order_id={order_id})")

    verdict = evaluate_call("issue_refund", {"amount": amount, "order_id": order_id})

    if verdict != "ALLOW":
        print(f"\n⛔ {verdict}")
        print("🔍 Triggering automated threat analysis...")

        analysis = analyze_threat({
            "tool": "issue_refund",
            "amount": amount,
            "limit": 50,
            "order_id": order_id,
        })

        return (
            f"ACCESS DENIED: POLICY VIOLATION. "
            f"Refund of ${amount} for order {order_id} was BLOCKED. "
            f"Policy limit is $50. "
            f"Threat Analysis: {analysis}"
        )

    print(f"\n✅ Refund of ${amount} for order {order_id} processed successfully!")
    return f"SUCCESS: Refund of ${amount} issued for order {order_id}."


# ============================================================================
# LANGCHAIN AGENT WITH BEDROCK
# ============================================================================

def _clean_response(text: str) -> str:
    """Strip <thinking>...</thinking> tags that some models leak."""
    return re.sub(r"<thinking>.*?</thinking>\s*", "", text, flags=re.DOTALL).strip()

# ── SAFETY LIMITS ─────────────────────────────────────────────
MAX_TURNS = 10          # Hard cap on conversation turns (protects AWS credits)
MAX_MESSAGES = 20       # Max messages in context (prevents context bloat)


def _trim_messages(messages: list, max_count: int = MAX_MESSAGES) -> list:
    """Keep the system prompt + last N messages to prevent context window bloat."""
    if len(messages) <= max_count:
        return messages
    # Always keep the system prompt (index 0), trim the middle
    return [messages[0]] + messages[-(max_count - 1):]


def run_langchain_agent():
    """Run the full LangChain agent with Bedrock and tool calling."""
    from langchain_core.messages import ToolMessage

    print("\n" + "=" * 60)
    print("🤖 SudoMode Retail Agent (LangChain + Bedrock)")
    print("=" * 60)
    print(f"   ⚠️  Safety: max {MAX_TURNS} turns, max_tokens=300 per call")

    # Initialize ChatBedrock with STRICT max_tokens to protect AWS credits
    llm = ChatBedrock(
        model_id="us.amazon.nova-pro-v1:0",
        region_name="us-east-1",
        model_kwargs={
            "max_tokens": 300,       # STRICT: cap output tokens per call
            "temperature": 0.1,
        },
    )

    # Bind the refund tool to the LLM
    tools = [issue_refund]
    llm_with_tools = llm.bind_tools(tools)

    # System prompt for the retail agent
    system_msg = SystemMessage(content=(
        "You are an AI customer service agent for a retail company. "
        "You help customers with refunds, order inquiries, and product questions. "
        "When a customer requests a refund, use the issue_refund tool. "
        "Always be polite and helpful. Keep responses under 2 sentences."
    ))

    print(f"\n💬 Type your message (or 'quit' to exit, max {MAX_TURNS} turns)")
    print("   Try: 'I need a refund of $500 for order ORD-7842'\n")

    # ── Chat loop with input() break + hard turn limit ──
    messages = [system_msg]
    turn_count = 0

    while turn_count < MAX_TURNS:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ("quit", "exit", "q"):
            print("\n👋 Goodbye!")
            break

        turn_count += 1
        print(f"   [Turn {turn_count}/{MAX_TURNS}]")

        messages.append(HumanMessage(content=user_input))
        messages = _trim_messages(messages)  # Prevent context bloat

        # Get LLM response (may include tool calls)
        try:
            response = llm_with_tools.invoke(messages)
        except Exception as e:
            print(f"\n❌ Bedrock error: {e}")
            print("   Skipping this turn. Try again or type 'quit'.")
            continue

        messages.append(response)

        # Check if the LLM wants to call a tool
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                print(f"\n🤖 Agent wants to call: {tool_name}({tool_call['args']})")

                # SAFETY: Only allow known tools
                if tool_name != "issue_refund":
                    print(f"⛔ Unknown tool '{tool_name}' — blocked by safety guard.")
                    tool_result = f"ERROR: Tool '{tool_name}' is not permitted."
                else:
                    tool_result = issue_refund.invoke(tool_call["args"])

                tool_msg = ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call["id"],
                )
                messages.append(tool_msg)

            # Get the final response after tool execution
            messages = _trim_messages(messages)  # Trim before second LLM call
            try:
                final_response = llm_with_tools.invoke(messages)
                messages.append(final_response)
                print(f"\n🤖 Agent: {_clean_response(final_response.content)}")
            except Exception as e:
                print(f"\n❌ Bedrock error on follow-up: {e}")

        else:
            # No tool call — just print the response
            print(f"\n🤖 Agent: {_clean_response(response.content)}")

        print()  # Blank line between turns

    else:
        # Reached MAX_TURNS — forced exit
        print(f"\n⚠️  Reached maximum {MAX_TURNS} turns. Session ended to protect AWS credits.")
        print("   Restart the demo to continue.")


# ============================================================================
# STANDALONE DEMO (no LangChain/Bedrock required)
# ============================================================================

def run_standalone_demo():
    """Run a simple demo without LangChain for environments without AWS."""
    print("\n" + "=" * 60)
    print("🤖 SudoMode Retail Agent (Standalone Demo)")
    print("=" * 60)
    print("\nSimulating the hackathon demo scenario...\n")

    # ── Scenario 1: Customer requests $500 refund (BLOCKED) ──
    print("📋 SCENARIO: Customer requests $500 refund for order ORD-7842")
    print("-" * 60)
    result = issue_refund_standalone(amount=500, order_id="ORD-7842")
    print(f"\n📝 Result: {result}")

    print("\n")

    # ── Scenario 2: Customer requests $30 refund (ALLOWED) ───
    print("📋 SCENARIO: Customer requests $30 refund for order ORD-1234")
    print("-" * 60)
    result = issue_refund_standalone(amount=30, order_id="ORD-1234")
    print(f"\n📝 Result: {result}")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point — choose LangChain or standalone mode."""
    print("=" * 60)
    print("🛡️  SudoMode — Autonomous Refund Agent Demo")
    print("=" * 60)

    if LANGCHAIN_AVAILABLE:
        print("\n1. Full LangChain Agent (requires AWS Bedrock)")
        print("2. Standalone Demo (no AWS needed)")
        print()

        choice = input("Select mode [1/2]: ").strip()

        if choice == "1":
            run_langchain_agent()
        else:
            run_standalone_demo()
    else:
        run_standalone_demo()


if __name__ == "__main__":
    main()
