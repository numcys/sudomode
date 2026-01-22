# SudoMode SDK

Python client library for SudoMode governance API.

## Installation

```bash
cd sdk
pip install -r requirements.txt
```

## Quick Start

```python
from sudomode import SudoClient

# Initialize client
client = SudoClient(base_url="http://localhost:8000")

# Check permission (low-level)
result = client.check("database", "read", {})
print(f"Status: {result.status}, Reason: {result.reason}")

# Execute with automatic error handling (high-level)
try:
    client.execute("database", "read", {})
    print("✅ Action allowed")
except PermissionError as e:
    print(f"⛔ Blocked: {e}")
except BlockingIOError as e:
    print(f"⏳ Approval required: {e}")
```

## API Reference

### `SudoClient(base_url="http://localhost:8000", api_key=None)`

Initialize the client.

### `check(resource, action, args=None) -> GovernanceResponse`

Low-level method that returns the full response from the server.

### `execute(resource, action, args=None) -> bool`

High-level helper that:
- Returns `True` if `ALLOW`
- Raises `PermissionError` if `DENY`
- Raises `BlockingIOError` if `REQUIRE_APPROVAL`

## Running the Demo

Make sure the SudoMode server is running on `http://localhost:8000`, then:

```bash
cd sdk
python examples/demo_agent.py
```

This will demonstrate all three scenarios:
1. ✅ Read operation (allowed)
2. ⛔ Delete operation (blocked)
3. ⏳ High-value charge (requires approval)

