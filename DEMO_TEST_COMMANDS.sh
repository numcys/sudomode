#!/bin/bash
# ============================================================================
# SudoMode Fresh Install Test - Copy-Paste Commands
# ============================================================================
# 
# Run these commands ONE BY ONE in a fresh terminal to test the installation.
# This simulates what a new user would experience.
#
# Prerequisites:
# - Python 3.11 or 3.12 installed
# - Node.js 18+ installed
# - Git installed
#
# ============================================================================

echo "🧪 SudoMode Fresh Install Test"
echo "================================"
echo ""
echo "This script will test a complete fresh installation."
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# ============================================================================
# STEP 1: Environment Setup
# ============================================================================
echo ""
echo "📁 STEP 1: Setting up test environment"
echo "----------------------------------------"

# Create clean test directory
TEST_DIR="/tmp/sudomode-demo-test"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "✅ Created test directory: $TEST_DIR"
echo ""

# ============================================================================
# STEP 2: Clone Repository
# ============================================================================
echo "📥 STEP 2: Cloning repository"
echo "----------------------------------------"
echo "⚠️  IMPORTANT: Replace 'yourusername' with your actual GitHub username"
echo ""

# For actual testing, uncomment and use your repo URL:
# git clone https://github.com/yourusername/sudomode-ai.git
# cd sudomode-ai

# For local testing (copy current repo):
echo "Copying current repository for testing..."
cp -r /Users/numcys/Github/PROJECTS/SudoMode/sudomode-ai "$TEST_DIR/" 2>/dev/null || {
    echo "❌ Could not copy repository. Please adjust the path or use git clone."
    exit 1
}
cd "$TEST_DIR/sudomode-ai"

echo "✅ Repository ready"
echo ""

# ============================================================================
# STEP 3: Server Setup (Backend)
# ============================================================================
echo "🖥️  STEP 3: Setting up Server (Backend)"
echo "----------------------------------------"

cd server

# Detect Python version
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
else
    PYTHON_CMD="python3"
    echo "⚠️  Warning: Using python3 (3.11 or 3.12 recommended)"
fi

echo "Using: $($PYTHON_CMD --version)"

# Create virtual environment
echo "Creating virtual environment..."
$PYTHON_CMD -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing server dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt

# Check/create policies.yaml
if [ ! -f "policies.yaml" ]; then
    echo "📋 Creating policies.yaml from example..."
    cp policies.yaml.example policies.yaml
fi

# Verify server setup
echo "Verifying server setup..."
python -c "from app.main import app; print('✅ Server setup successful')" || {
    echo "❌ Server setup failed"
    exit 1
}

echo "✅ Server setup complete"
echo ""

# ============================================================================
# STEP 4: SDK Setup (Client Library)
# ============================================================================
echo "📦 STEP 4: Setting up SDK (Client Library)"
echo "----------------------------------------"

cd ../sdk

# Install SDK as package
echo "Installing SDK as package..."
pip install -e . --quiet

# Verify import
echo "Testing SDK import..."
python -c "from sudomode import SudoClient; print('✅ SDK import successful')" || {
    echo "❌ SDK import failed"
    exit 1
}

echo "✅ SDK setup complete"
echo ""

# ============================================================================
# STEP 5: Dashboard Setup (Frontend)
# ============================================================================
echo "🎨 STEP 5: Setting up Dashboard (Frontend)"
echo "----------------------------------------"

cd ../dashboard

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo "Using Node.js: $(node --version)"

# Install dependencies
echo "Installing npm dependencies..."
npm install --silent

echo "✅ Dashboard setup complete"
echo ""

# ============================================================================
# STEP 6: Final Verification
# ============================================================================
echo "✅ STEP 6: Final Verification"
echo "----------------------------------------"

cd ..

echo "Checking critical files..."
FILES=(
    "server/policies.yaml"
    "server/app/main.py"
    "sdk/sudomode/client.py"
    "sdk/examples/demo_agent.py"
    "dashboard/package.json"
)

ALL_OK=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING)"
        ALL_OK=false
    fi
done

if [ "$ALL_OK" = false ]; then
    echo ""
    echo "❌ Some files are missing. Please check the repository."
    exit 1
fi

echo ""
echo "🎉 Setup Complete!"
echo "================================"
echo ""
echo "Next steps to test the full flow:"
echo ""
echo "TERMINAL 1 - Start Server:"
echo "  cd $TEST_DIR/sudomode-ai/server"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "TERMINAL 2 - Start Dashboard (optional):"
echo "  cd $TEST_DIR/sudomode-ai/dashboard"
echo "  npm run dev"
echo ""
echo "TERMINAL 3 - Run Demo:"
echo "  cd $TEST_DIR/sudomode-ai/sdk"
echo "  source ../server/venv/bin/activate"
echo "  python examples/demo_agent.py"
echo ""
echo "Test directory: $TEST_DIR/sudomode-ai"
echo ""

