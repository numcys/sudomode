#!/bin/bash
# Test script for state management endpoints

BASE_URL="http://localhost:8000"

echo "Testing SudoMode State Management"
echo "=================================="
echo ""

# Step 1: Make a high-value charge request (should require approval)
echo "Step 1: Making a high-value charge request..."
RESPONSE=$(curl -s -X POST "$BASE_URL/v1/govern" \
  -H "Content-Type: application/json" \
  -d '{
    "resource": "stripe.charge",
    "action": "charge",
    "args": {"amount": 5000}
  }')

echo "$RESPONSE" | python3 -m json.tool
echo ""

# Extract request_id from response (if present)
REQUEST_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('request_id', ''))" 2>/dev/null)

if [ -z "$REQUEST_ID" ]; then
    echo "⚠️  No request_id returned. Make sure the request requires approval."
    exit 1
fi

echo "Request ID: $REQUEST_ID"
echo ""

# Step 2: List all pending requests
echo "Step 2: Listing all pending requests..."
curl -s -X GET "$BASE_URL/v1/requests" | python3 -m json.tool
echo ""

# Step 3: Approve the request
echo "Step 3: Approving request $REQUEST_ID..."
curl -s -X POST "$BASE_URL/v1/requests/$REQUEST_ID/approve" | python3 -m json.tool
echo ""

# Step 4: List requests again (should show approved status)
echo "Step 4: Listing requests again (should show approved)..."
curl -s -X GET "$BASE_URL/v1/requests" | python3 -m json.tool
echo ""

echo "✅ State management test complete!"


