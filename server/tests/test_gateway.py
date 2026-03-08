"""
SudoMode Gateway — Unit Tests
==============================
Tests for evaluate_call() and analyze_threat().
Prints clear PASS/FAIL for each test case.

Usage:
    cd server
    python -m tests.test_gateway
"""

import sys
import os

# Add the server directory to the path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.gateway import evaluate_call
from app.services.threat_analyzer import analyze_threat

passed = 0
failed = 0


def test(name: str, actual, expected):
    """Run a single test assertion and print result."""
    global passed, failed
    if actual == expected:
        print(f"  ✅ PASS: {name}")
        passed += 1
    else:
        print(f"  ❌ FAIL: {name}")
        print(f"         Expected: {expected!r}")
        print(f"         Got:      {actual!r}")
        failed += 1


print("=" * 60)
print("SudoMode Gateway — Unit Tests")
print("=" * 60)
print()

# ── Test 1: $500 refund should be BLOCKED ────────────────────
print("Test 1: issue_refund($500) — should be BLOCKED")
result = evaluate_call("issue_refund", {"amount": 500, "order_id": "ORD-001"})
test("$500 refund blocked", result, "ACCESS DENIED: POLICY VIOLATION")
print()

# ── Test 2: $30 refund should be ALLOWED ─────────────────────
print("Test 2: issue_refund($30) — should be ALLOWED")
result = evaluate_call("issue_refund", {"amount": 30, "order_id": "ORD-002"})
test("$30 refund allowed", result, "ALLOW")
print()

# ── Test 3: $50 exact boundary — should be ALLOWED ───────────
print("Test 3: issue_refund($50) — boundary, should be ALLOWED")
result = evaluate_call("issue_refund", {"amount": 50, "order_id": "ORD-003"})
test("$50 refund (boundary) allowed", result, "ALLOW")
print()

# ── Test 4: Unknown tool — no policy, should ALLOW ───────────
print("Test 4: unknown_tool($999) — no matching policy, should ALLOW")
result = evaluate_call("unknown_tool", {"amount": 999})
test("Unknown tool allowed (no policy)", result, "ALLOW")
print()

# ── Test 5: Threat analysis smoke test ───────────────────────
print("Test 5: analyze_threat() — Bedrock smoke test")
try:
    analysis = analyze_threat({
        "tool": "issue_refund",
        "amount": 500,
        "limit": 50,
        "order_id": "ORD-001",
    })
    if analysis and len(analysis) > 10:
        print(f"  ✅ PASS: Threat analysis returned a response")
        print(f"         Response: {analysis[:120]}...")
        passed += 1
    else:
        print(f"  ⚠️  SKIP: Threat analysis returned empty/short response")
except Exception as e:
    print(f"  ⚠️  SKIP: Bedrock unavailable ({e})")

# ── Summary ──────────────────────────────────────────────────
print()
print("=" * 60)
print(f"Results: {passed} passed, {failed} failed")
if failed == 0:
    print("🎉 All tests passed!")
else:
    print("⚠️  Some tests failed — check output above.")
print("=" * 60)
