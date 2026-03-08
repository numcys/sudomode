"""
SudoMode Gateway — Zero-Trust Policy Evaluation for Agent Tool Calls
=====================================================================
Intercepts autonomous agent tool calls, evaluates them against local
policy rules, and blocks rogue actions before execution.

This module extends the existing PolicyEngine (engine.py) with a
direct tool-call interception model for the hackathon demo scenario.

Components:
  1. POLICY_STORE       — Mock policy database (replaces DynamoDB for demo)
  2. evaluate_call()    — Core tool-call policy evaluation
"""


# ============================================================================
# 1. MOCK POLICY STORE
# ============================================================================
# In production this would be DynamoDB. For the hackathon demo, we use a
# local list of policy dicts. Each policy defines a target function,
# a max_amount threshold, and the action to take when exceeded.

POLICY_STORE = [
    {
        "target": "issue_refund",
        "max_amount": 50,
        "action": "BLOCK",
    }
]


# ============================================================================
# 2. TOOL-CALL POLICY EVALUATION
# ============================================================================

def evaluate_call(tool_name: str, arguments: dict) -> str:
    """
    Evaluate an agent's tool call against the policy store.

    This is the core interception function. When a LangChain agent
    invokes a tool, the tool's internal logic calls this function
    BEFORE executing any real operation.

    Args:
        tool_name:  Name of the tool the agent is trying to call
                    (e.g., "issue_refund").
        arguments:  Dict of arguments the agent passed
                    (e.g., {"amount": 500, "order_id": "ORD-123"}).

    Returns:
        "ACCESS DENIED: POLICY VIOLATION" — if the call violates a policy.
        "ALLOW"                           — if no policy blocks the call.
    """
    for policy in POLICY_STORE:
        # Check if this policy applies to the requested tool
        if policy["target"] != tool_name:
            continue

        # Check if the amount exceeds the policy threshold
        amount = arguments.get("amount", 0)
        if amount > policy["max_amount"]:
            print(f"\n{'='*60}")
            print(f"🛡️  SUDOMODE GATEWAY — POLICY CHECK")
            print(f"{'='*60}")
            print(f"  Tool:       {tool_name}")
            print(f"  Amount:     ${amount}")
            print(f"  Limit:      ${policy['max_amount']}")
            print(f"  Action:     {policy['action']}")
            print(f"  Verdict:    ⛔ ACCESS DENIED: POLICY VIOLATION")
            print(f"{'='*60}\n")
            return "ACCESS DENIED: POLICY VIOLATION"

    # No policy matched or all checks passed
    print(f"\n{'='*60}")
    print(f"🛡️  SUDOMODE GATEWAY — POLICY CHECK")
    print(f"{'='*60}")
    print(f"  Tool:       {tool_name}")
    print(f"  Amount:     ${arguments.get('amount', 'N/A')}")
    print(f"  Verdict:    ✅ ALLOW")
    print(f"{'='*60}\n")
    return "ALLOW"
