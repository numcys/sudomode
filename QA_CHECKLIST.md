# QA Checklist: Fresh Install Test

## Pre-Test Requirements
- [ ] Python 3.11 or 3.12 installed
- [ ] Node.js 18+ installed
- [ ] npm installed
- [ ] Clean temporary directory for testing

## Test Environment Setup

### Step 1: Clone Repository
```bash
# Create test directory
cd /tmp
rm -rf sudomode-test
git clone <your-repo-url> sudomode-test
cd sudomode-test
```

### Step 2: Server Setup
- [ ] Create virtual environment
- [ ] Install server dependencies
- [ ] Copy `policies.yaml.example` to `policies.yaml` (if needed)
- [ ] Verify `policies.yaml` exists
- [ ] Test server starts without errors

### Step 3: SDK Setup
- [ ] Install SDK dependencies
- [ ] Verify `demo_agent.py` can import `sudomode`
- [ ] Test SDK installation method (pip install -e . vs requirements.txt)

### Step 4: Dashboard Setup
- [ ] Install npm dependencies
- [ ] Verify dashboard starts without errors
- [ ] Test dashboard connects to server

### Step 5: Full Integration Test
- [ ] Start server
- [ ] Start dashboard (optional)
- [ ] Run demo_agent.py
- [ ] Verify requests appear in dashboard
- [ ] Test approve/reject flow

## Potential Issues to Check

1. **Missing policies.yaml** - Server needs this file
2. **SDK import errors** - demo_agent.py needs sudomode package
3. **Port conflicts** - 8000 (server) and 5173 (dashboard)
4. **Python version** - Must be 3.11 or 3.12
5. **Missing .env** - Optional but should be documented

