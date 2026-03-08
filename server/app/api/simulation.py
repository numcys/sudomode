"""
SudoMode Chat Simulation & Policies API
=========================================
Endpoints for the dashboard's "Live Simulation" and "Active Policies" views.

Supports three governance outcomes:
  - ALLOW:            refund ≤ $20, auto-approved
  - REQUIRE_APPROVAL: $20 < refund ≤ $100, routed to human
  - DENY:             refund > $100, hard denied + threat analysis
"""

import re
import uuid
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter

from app.core.engine import PolicyEngine
from app.core.store import add_request, get_request
from app.api.models import GovernanceRequest
from app.services.threat_analyzer import analyze_threat

router = APIRouter(prefix="/api/v1", tags=["simulation"])

# Use the real policy engine (reads policies.yaml)
engine = PolicyEngine()


# ── Request / Response models ────────────────────────────────

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    agent_reply: str
    gateway_triggered: bool
    gateway_action: Optional[str] = None
    threat_analysis: Optional[str] = None
    attempted_amount: Optional[float] = None
    request_id: Optional[str] = None


class PollResponse(BaseModel):
    status: str
    agent_reply: Optional[str] = None


# ── Helper: extract refund intent ────────────────────────────

def _parse_refund_request(message: str) -> tuple[bool, float, str]:
    amount_match = re.search(
        r'\$\s?(\d+(?:\.\d{2})?)|(\d+(?:\.\d{2})?)\s*(?:dollars?|usd)',
        message, re.IGNORECASE,
    )
    order_match = re.search(
        r'(?:ORD-?\d+|order\s*#?\s*(\d+)|#(\d+))',
        message, re.IGNORECASE,
    )
    refund_keywords = ['refund', 'return', 'money back', 'reimburse', 'credit back', 'chargeback']
    is_refund = any(kw in message.lower() for kw in refund_keywords)

    amount = 0.0
    if amount_match:
        amount = float(amount_match.group(1) or amount_match.group(2))

    order_id = "ORD-0000"
    if order_match:
        order_id = order_match.group(0)

    return is_refund, amount, order_id


# ── Chat Simulation Endpoint ─────────────────────────────────

@router.post("/chat-simulation", response_model=ChatResponse)
async def chat_simulation(request: ChatRequest):
    message = request.message.strip()
    is_refund, amount, order_id = _parse_refund_request(message)

    if not is_refund or amount <= 0:
        return ChatResponse(
            agent_reply=(
                "I'm your AI customer service agent! I can help you with refunds, "
                "order inquiries, and product questions. How can I assist you today?"
            ),
            gateway_triggered=False,
        )

    # Route through the real policy engine
    gov_request = GovernanceRequest(
        resource="payment",
        action="issue_refund",
        args={"amount": amount, "order_id": order_id},
    )
    result = engine.evaluate(gov_request)

    if result.status == "REQUIRE_APPROVAL":
        request_id = str(uuid.uuid4())
        add_request(
            request_id=request_id,
            request=gov_request,
            status="PENDING",
            reason=result.reason,
        )
        return ChatResponse(
            agent_reply=(
                f"Your refund of ${amount:.2f} for order {order_id} "
                f"requires manager approval. A supervisor has been notified — "
                f"please wait while they review your request."
            ),
            gateway_triggered=True,
            gateway_action="PENDING",
            attempted_amount=amount,
            request_id=request_id,
        )

    elif result.status == "DENY":
        analysis = analyze_threat({
            "tool": "issue_refund",
            "amount": amount,
            "limit": 100,
            "order_id": order_id,
        })
        return ChatResponse(
            agent_reply=(
                f"I'm sorry, but a refund of ${amount:.2f} for order {order_id} "
                f"has been blocked. This exceeds the $100 hard limit. "
                "This incident has been logged for security review."
            ),
            gateway_triggered=True,
            gateway_action="DENY",
            threat_analysis=analysis,
            attempted_amount=amount,
        )

    else:  # ALLOW
        return ChatResponse(
            agent_reply=(
                f"Your refund of ${amount:.2f} for order {order_id} has been "
                f"auto-approved. The amount will be credited back within 3-5 business days."
            ),
            gateway_triggered=True,
            gateway_action="ALLOW",
            attempted_amount=amount,
        )


# ── Approval Polling Endpoint ────────────────────────────────

@router.get("/simulation/poll/{request_id}", response_model=PollResponse)
async def poll_approval(request_id: str):
    req = get_request(request_id)
    if not req:
        return PollResponse(status="NOT_FOUND")

    status = req.get("status", "PENDING")

    if status == "APPROVED":
        return PollResponse(
            status="APPROVED",
            agent_reply="Great news! Your refund has been approved by a manager and will be processed shortly.",
        )
    elif status == "REJECTED":
        return PollResponse(
            status="REJECTED",
            agent_reply="Your refund request has been rejected by a manager. Please contact support.",
        )
    return PollResponse(status="PENDING")


# ── Active Policies Endpoint ─────────────────────────────────

@router.get("/policies")
async def get_policies():
    """Return the active 3-tier policy configuration as structured JSON."""
    return {
        "policy_name": "SudoMode Retail Refund Policy v2.0",
        "description": "Multi-tier escalation matrix for AI agent refund operations",
        "last_updated": "2026-03-08T14:00:00Z",
        "enforcement": "ACTIVE",
        "rules": [
            {
                "id": "POL-001",
                "name": "Auto-Approve Small Refunds",
                "resource": "payment",
                "action": "issue_refund",
                "condition": "amount ≤ $20",
                "decision": "ALLOW",
                "color": "green",
                "description": "Refunds of $20 or less are automatically approved without human intervention.",
                "risk_level": "LOW",
            },
            {
                "id": "POL-002",
                "name": "Manager Approval Required",
                "resource": "payment",
                "action": "issue_refund",
                "condition": "$20 < amount ≤ $100",
                "decision": "REQUIRE_APPROVAL",
                "color": "yellow",
                "description": "Mid-range refunds are paused and routed to the Human-in-the-Loop (HITL) approval queue for manager review.",
                "risk_level": "MEDIUM",
            },
            {
                "id": "POL-003",
                "name": "Hard Deny + Threat Analysis",
                "resource": "payment",
                "action": "issue_refund",
                "condition": "amount > $100",
                "decision": "DENY",
                "color": "red",
                "description": "High-value refund requests are immediately blocked. An automated SOC threat analysis is triggered via Amazon Bedrock.",
                "risk_level": "HIGH",
            },
            {
                "id": "POL-004",
                "name": "Default Deny All",
                "resource": "*",
                "action": "*",
                "condition": "No matching rule",
                "decision": "DENY",
                "color": "red",
                "description": "Any unrecognized AI agent action is denied by default (Zero-Trust).",
                "risk_level": "CRITICAL",
            },
        ],
    }
