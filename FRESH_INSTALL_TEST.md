# Fresh Install Test - Exact Commands

## 🎯 Purpose
Test that a completely fresh user can clone and run SudoMode without errors.

## 📋 Prerequisites Check
```bash
# Verify Python 3.11 or 3.12
python3.11 --version || python3.12 --version

# Verify Node.js 18+
node --version

# Verify npm
npm --version
```

---

## 🧪 Complete Test Sequence

### Step 1: Create Clean Test Environment
```bash
# Create temporary test directory
cd /tmp
rm -rf sudomode-fresh-test
mkdir sudomode-fresh-test
cd sudomode-fresh-test

# Clone your repository (replace with actual URL)
git clone https://github.com/yourusername/sudomode-ai.git
cd sudomode-ai
```

### Step 2: Server Setup (Backend)
```bash
# Navigate to server directory
cd server

# Create virtual environment
python3.11 -m venv venv
# OR if 3.11 not available:
# python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate
# Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install server dependencies
pip install -r requirements.txt

# Verify policies.yaml exists (copy from example if needed)
if [ ! -f "policies.yaml" ]; then
    echo "⚠️  policies.yaml not found, copying from example..."
    cp policies.yaml.example policies.yaml
fi

# Verify server can start (quick test)
python -c "from app.main import app; print('✅ Server imports successful')"
```

### Step 3: SDK Setup (Client Library)
```bash
# Navigate to SDK directory
cd ../sdk

# Install SDK as a package (recommended method)
pip install -e .

# Verify SDK import works
python -c "from sudomode import SudoClient; print('✅ SDK import successful')"
```

**Alternative SDK Setup (if pip install -e . fails):**
```bash
# Install SDK dependencies only
pip install -r requirements.txt

# Test import (should work with sys.path in demo_agent.py)
python -c "import sys; sys.path.insert(0, '.'); from sudomode import SudoClient; print('✅ SDK import successful')"
```

### Step 4: Dashboard Setup (Frontend)
```bash
# Navigate to dashboard directory
cd ../dashboard

# Install npm dependencies
npm install

# Verify package.json is valid
npm list --depth=0
```

### Step 5: Configuration Check
```bash
# Go back to root
cd ..

# Verify all critical files exist
echo "Checking critical files..."
[ -f "server/policies.yaml" ] && echo "✅ server/policies.yaml" || echo "❌ server/policies.yaml MISSING"
[ -f "sdk/examples/demo_agent.py" ] && echo "✅ sdk/examples/demo_agent.py" || echo "❌ demo_agent.py MISSING"
[ -f "dashboard/package.json" ] && echo "✅ dashboard/package.json" || echo "❌ package.json MISSING"
```

---

## 🚀 Full Integration Test

### Terminal 1: Start Server
```bash
cd /tmp/sudomode-fresh-test/sudomode-ai/server
source venv/bin/activate
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Test server health:**
```bash
# In another terminal, test the health endpoint
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Terminal 2: Start Dashboard (Optional)
```bash
cd /tmp/sudomode-fresh-test/sudomode-ai/dashboard
npm run dev
```

**Expected output:**
```
VITE v7.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

### Terminal 3: Run Demo
```bash
cd /tmp/sudomode-fresh-test/sudomode-ai/sdk
source ../server/venv/bin/activate  # Use server's venv (has all deps)
python examples/demo_agent.py
```

**Expected output:**
```
🤖 Rogue AI Agent Starting...
============================================================

📖 Scenario 1: Agent tries to READ database...
✅ Success: Database read operation allowed

🗑️  Scenario 2: Agent tries to DELETE database...
⛔ Blocked by SudoMode: Permission denied: Delete operations on database are forbidden

💰 Scenario 3: Agent tries to TRANSFER $5000...
⏳ SudoMode: Paused. Waiting for approval (ID: ...)...
```

**Verify in Dashboard:**
- Open http://localhost:5173
- Should see pending request appear automatically
- Click "AUTHORIZE" or "BLOCK" to test approval flow

---

## ✅ Success Criteria

- [ ] Server starts without errors
- [ ] Server health endpoint returns `{"status":"healthy"}`
- [ ] Dashboard starts without errors
- [ ] Dashboard loads at http://localhost:5173
- [ ] SDK imports successfully (`from sudomode import SudoClient`)
- [ ] `demo_agent.py` runs without import errors
- [ ] Demo creates a pending request
- [ ] Request appears in dashboard
- [ ] Approve/reject buttons work in dashboard

---

## 🐛 Common Issues & Fixes

### Issue: `policies.yaml` not found
**Fix:**
```bash
cd server
cp policies.yaml.example policies.yaml
```

### Issue: SDK import fails
**Fix:**
```bash
cd sdk
pip install -e .
# OR
pip install -r requirements.txt
```

### Issue: Port 8000 already in use
**Fix:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
# OR change port in server/app/main.py
```

### Issue: Python version incompatible
**Fix:**
```bash
# Use Python 3.11 or 3.12 specifically
python3.11 -m venv venv
# OR
python3.12 -m venv venv
```

### Issue: npm install fails
**Fix:**
```bash
# Clear npm cache
npm cache clean --force
# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 📝 Notes for Demo Video

1. **Start with prerequisites check** - Show Python and Node versions
2. **Show the clone command** - Make it clear this is a fresh install
3. **Highlight the policies.yaml setup** - Important configuration step
4. **Demonstrate the three-terminal setup** - Server, Dashboard, Demo
5. **Show the real-time dashboard update** - Request appearing automatically
6. **Test the approve flow** - Click authorize and see agent resume

---

## 🎬 Quick Demo Script

```bash
# 1. Clone (5 seconds)
git clone https://github.com/yourusername/sudomode-ai.git
cd sudomode-ai

# 2. Server setup (10 seconds)
cd server && python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp policies.yaml.example policies.yaml  # If needed

# 3. SDK setup (5 seconds)
cd ../sdk && pip install -e .

# 4. Dashboard setup (10 seconds)
cd ../dashboard && npm install

# 5. Start everything (show in split screen)
# Terminal 1: uvicorn app.main:app --reload
# Terminal 2: npm run dev
# Terminal 3: python examples/demo_agent.py
```

**Total setup time: ~30 seconds** (excluding download time)

