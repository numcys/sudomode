"""
SudoMode Live Demo: Human-in-the-Loop Refund Agent
====================================================

This demo uses the LIVE SudoMode server + dashboard to show the full
human-in-the-loop governance flow:

  1. Agent tries to issue a $500 refund via the LangChain tool
  2. SudoMode server evaluates the policy → REQUIRE_APPROVAL
  3. Request appears in the dashboard at http://localhost:5173
  4. Agent PAUSES and polls while waiting for a human to approve/reject
  5. Human clicks Approve/Reject on the dashboard
  6. Agent resumes and reports the outcome

Prerequisites:
--------------
1. Start the SudoMode server:
     cd server && uvicorn app.main:app --reload

2. Start the dashboard:
     cd dashboard && npm run dev

3. Install SDK dependencies:
     cd sdk && pip install -r requirements.txt

Usage:
------
    cd sdk
    python examples/retail_agent_live.py
"""

import sys
import re
import logging
from pathlib import Path

# Add sdk/ to path for sudomode imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sudomode import SudoClient
from sudomode.client import configure_logging

# ── LangChain + Bedrock imports ──────────────────────────────
try:
    from langchain_aws import ChatBedrock
    from langchain_core.tools import tool
    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️  langchain-aws not installed. Install with: pip install langchain-aws langchain-core")

# ── SudoMode client (talks to live server) ───────────────────
sudo_client = SudoClient(base_url="http://localhost:8000")
configure_logging(level=logging.INFO)

# ── Safety limits ────────────────────────────────────────────
MAX_TURNS = 10
MAX_MESSAGES = 20


def _clean_response(text: str) -> str:
    """Strip <thinking>...</thinking> tags that some models leak."""
    return re.sub(r"<thinking>.*?</thinking>\s*", "", text, flags=re.DOTALL).strip()


def _trim_messages(messages: list, max_count: int = MAX_MESSAGES) -> list:
    """Keep system prompt + last N messages to prevent context bloat."""
    if len(messages) <= max_count:
        return messages
    return [messages[0]] + messages[-(max_count - 1):]


# ============================================================================
# THE TOOL: issue_refund — routed through LIVE SudoMode server
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
        print(f"📡 Sending to SudoMode server for policy evaluation...")

        try:
            # Route through the LIVE SudoMode server API
            # This calls POST /v1/govern with the action details
            # If REQUIRE_APPROVAL, it will BLOCK here and poll until approved/rejected
            result = sudo_client.execute(
                resource="payment",
                action="issue_refund",
                args={"amount": amount, "order_id": order_id},
                poll_interval=3,  # Check every 3 seconds
            )

            if result:
                print(f"\n✅ Refund of ${amount} for order {order_id} APPROVED and processed!")
                return f"SUCCESS: Refund of ${amount} issued for order {order_id}. A human reviewer approved this transaction."

        except PermissionError as e:
            print(f"\n⛔ {e}")
            return (
                f"DENIED: Refund of ${amount} for order {order_id} was rejected. "
                f"Reason: {e}"
            )

        except Exception as e:
            print(f"\n❌ Error communicating with SudoMode server: {e}")
            return (
                f"ERROR: Could not process refund. "
                f"Make sure the SudoMode server is running on http://localhost:8000. "
                f"Error: {e}"
            )


# ============================================================================
# STANDALONE FALLBACK (no LangChain)
# ============================================================================

def issue_refund_standalone(amount: float, order_id: str) -> str:
    """Standalone version that calls the live server directly."""
    print(f"\n🔄 Agent is attempting: issue_refund(amount=${amount}, order_id={order_id})")
    print(f"📡 Sending to SudoMode server...")

    try:
        result = sudo_client.execute(
            resource="payment",
            action="issue_refund",
            args={"amount": amount, "order_id": order_id},
            poll_interval=3,
        )
        if result:
            print(f"\n✅ Refund APPROVED and processed!")
            return f"SUCCESS: Refund of ${amount} issued for order {order_id}."

    except PermissionError as e:
        print(f"\n⛔ {e}")
        return f"DENIED: {e}"

    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return f"ERROR: {e}"


# ============================================================================
# LANGCHAIN AGENT (LIVE MODE)
# ============================================================================

def run_langchain_agent():
    """Run the LangChain agent with live SudoMode server integration."""
    print("\n" + "=" * 60)
    print("🤖 SudoMode Retail Agent (LIVE — Human-in-the-Loop)")
    print("=" * 60)
    print(f"   ⚠️  Safety: max {MAX_TURNS} turns, max_tokens=300 per call")
    print(f"   📡 Server: http://localhost:8000")
    print(f"   🖥️  Dashboard: http://localhost:5173")

    llm = ChatBedrock(
        model_id="us.amazon.nova-pro-v1:0",
        region_name="us-east-1",
        model_kwargs={
            "max_tokens": 300,
            "temperature": 0.1,
        },
    )

    tools = [issue_refund]
    llm_with_tools = llm.bind_tools(tools)

    system_msg = SystemMessage(content=(
        "You are an AI customer service agent for a retail company. "
        "You help customers with refunds. "
        "When a customer requests a refund, use the issue_refund tool. "
        "Keep responses under 2 sentences."
    ))

    print(f"\n💬 Type your message (or 'quit' to exit)")
    print(f"   Try: 'I need a refund of $500 for order ORD-7842'")
    print(f"\n   ⏳ For $500+, the agent will PAUSE until you")
    print(f"      approve/reject on the dashboard!\n")

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
        messages = _trim_messages(messages)

        try:
            response = llm_with_tools.invoke(messages)
        except Exception as e:
            print(f"\n❌ Bedrock error: {e}")
            continue

        messages.append(response)

        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                print(f"\n🤖 Agent wants to call: {tool_name}({tool_call['args']})")

                if tool_name != "issue_refund":
                    print(f"⛔ Unknown tool '{tool_name}' — blocked.")
                    tool_result = f"ERROR: Tool '{tool_name}' is not permitted."
                else:
                    tool_result = issue_refund.invoke(tool_call["args"])

                tool_msg = ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call["id"],
                )
                messages.append(tool_msg)

            messages = _trim_messages(messages)
            try:
                final_response = llm_with_tools.invoke(messages)
                messages.append(final_response)
                print(f"\n🤖 Agent: {_clean_response(final_response.content)}")
            except Exception as e:
                print(f"\n❌ Bedrock error: {e}")
        else:
            print(f"\n🤖 Agent: {_clean_response(response.content)}")

        print()

    else:
        print(f"\n⚠️  Reached maximum {MAX_TURNS} turns.")

    sudo_client.close()


# ============================================================================
# STANDALONE DEMO
# ============================================================================

def run_standalone_demo():
    """Run the standalone demo against the live server."""
    print("\n" + "=" * 60)
    print("🤖 SudoMode Retail Agent (LIVE — Standalone)")
    print("=" * 60)
    print(f"   📡 Server: http://localhost:8000")
    print(f"   🖥️  Dashboard: http://localhost:5173\n")

    # ── Scenario 1: $30 refund (should auto-approve) ──
    print("📋 SCENARIO 1: $30 refund (should be auto-approved)")
    print("-" * 60)
    result = issue_refund_standalone(amount=30, order_id="ORD-1234")
    print(f"📝 Result: {result}\n")

    # ── Scenario 2: $500 refund (requires human approval) ──
    print("📋 SCENARIO 2: $500 refund (requires HUMAN APPROVAL)")
    print("-" * 60)
    print("   👉 Go to http://localhost:5173 and approve/reject!")
    result = issue_refund_standalone(amount=500, order_id="ORD-7842")
    print(f"📝 Result: {result}\n")

    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)
    sudo_client.close()


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("🛡️  SudoMode — Human-in-the-Loop Refund Demo (LIVE)")
    print("=" * 60)
    print("\n⚠️  Make sure the server and dashboard are running!")
    print("   Server:    cd server && uvicorn app.main:app --reload")
    print("   Dashboard: cd dashboard && npm run dev")

    if LANGCHAIN_AVAILABLE:
        print("\n1. Full LangChain Agent (Bedrock + Live Server)")
        print("2. Standalone Demo (Live Server, no Bedrock)")
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
