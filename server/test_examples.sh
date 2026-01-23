#!/bin/bash
# Example curl commands to test the SudoMode API

BASE_URL="http://localhost:8000"

echo "Testing SudoMode Governance API"
echo "================================"
echo ""

# Test 1: Allow read on database
echo "Test 1: Read operation on database (should ALLOW)"
curl -X POST "$BASE_URL/v1/govern" \
  -H "Content-Type: application/json" \
  -d '{
    "resource": "database",
    "action": "read",
    "args": {}
  }'
echo -e "\n\n"

# Test 2: Deny delete on database
echo "Test 2: Delete operation on database (should DENY)"
curl -X POST "$BASE_URL/v1/govern" \
  -H "Content-Type: application/json" \
  -d '{
    "resource": "database",
    "action": "delete",
    "args": {}
  }'
echo -e "\n\n"

# Test 3: Low amount stripe charge (should ALLOW)
echo "Test 3: Low amount stripe charge - $30 (should ALLOW)"
curl -X POST "$BASE_URL/v1/govern" \
  -H "Content-Type: application/json" \
  -d '{
    "resource": "stripe.charge",
    "action": "charge",
    "args": {"amount": 30}
  }'
echo -e "\n\n"

# Test 4: High amount stripe charge (should REQUIRE_APPROVAL)
echo "Test 4: High amount stripe charge - $100 (should REQUIRE_APPROVAL)"
curl -X POST "$BASE_URL/v1/govern" \
  -H "Content-Type: application/json" \
  -d '{
    "resource": "stripe.charge",
    "action": "charge",
    "args": {"amount": 100}
  }'
echo -e "\n\n"

# Test 5: Unknown operation (should DENY - default)
echo "Test 5: Unknown operation (should DENY - default)"
curl -X POST "$BASE_URL/v1/govern" \
  -H "Content-Type: application/json" \
  -d '{
    "resource": "unknown",
    "action": "unknown",
    "args": {}
  }'
echo -e "\n\n"

echo "Tests complete!"

