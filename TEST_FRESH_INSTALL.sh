#!/bin/bash
# Fresh Install Test Script for SudoMode
# Run this in a clean temporary directory to simulate a new user experience

set -e  # Exit on error

echo "🧪 SudoMode Fresh Install Test"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test directory
TEST_DIR="/tmp/sudomode-fresh-test"
REPO_URL="."  # Change this to your actual repo URL for real testing

echo "📁 Step 1: Setting up test directory"
echo "-----------------------------------"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# If testing with actual git clone, uncomment:
# git clone "$REPO_URL" sudomode-ai
# cd sudomode-ai

# For local testing, copy current directory:
echo "Copying current directory to test location..."
cp -r /Users/numcys/Github/PROJECTS/SudoMode/sudomode-ai/* "$TEST_DIR/" 2>/dev/null || {
    echo "⚠️  Note: Adjust the path above to your actual repo location"
    echo "Or uncomment the git clone line for real testing"
}

cd "$TEST_DIR"
echo "✅ Test directory ready: $TEST_DIR"
echo ""

# Check Python version
echo "🐍 Step 2: Checking Python version"
echo "-----------------------------------"
PYTHON_CMD="python3.11"
if ! command -v "$PYTHON_CMD" &> /dev/null; then
    PYTHON_CMD="python3.12"
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        PYTHON_CMD="python3"
        echo "${YELLOW}⚠️  Warning: python3.11/3.12 not found, using python3${NC}"
    fi
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "Using: $PYTHON_VERSION"
echo ""

# Server setup
echo "🖥️  Step 3: Setting up Server (Backend)"
echo "-----------------------------------"
cd "$TEST_DIR/server"

# Create venv
echo "Creating virtual environment..."
$PYTHON_CMD -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing server dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if policies.yaml exists, if not copy from example
if [ ! -f "policies.yaml" ]; then
    echo "📋 Copying policies.yaml.example to policies.yaml..."
    cp policies.yaml.example policies.yaml
fi

echo "✅ Server setup complete"
echo ""

# SDK setup
echo "📦 Step 4: Setting up SDK (Client Library)"
echo "-----------------------------------"
cd "$TEST_DIR/sdk"

# Option 1: Install as package (recommended)
echo "Installing SDK as package..."
pip install -e .

# Verify import works
echo "Testing SDK import..."
python3 -c "from sudomode import SudoClient; print('✅ SDK import successful')" || {
    echo "${RED}❌ SDK import failed${NC}"
    exit 1
}

echo "✅ SDK setup complete"
echo ""

# Dashboard setup
echo "🎨 Step 5: Setting up Dashboard (Frontend)"
echo "-----------------------------------"
cd "$TEST_DIR/dashboard"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "Using Node.js: $NODE_VERSION"

# Install dependencies
echo "Installing npm dependencies..."
npm install

echo "✅ Dashboard setup complete"
echo ""

# Final verification
echo "✅ Step 6: Verification"
echo "-----------------------------------"
echo "Checking file structure..."

# Check critical files
FILES_TO_CHECK=(
    "server/policies.yaml"
    "server/app/main.py"
    "sdk/sudomode/client.py"
    "sdk/examples/demo_agent.py"
    "dashboard/package.json"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$TEST_DIR/$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ${RED}❌ $file (MISSING)${NC}"
    fi
done

echo ""
echo "🎉 Setup Complete!"
echo "================================"
echo ""
echo "Next steps to test:"
echo ""
echo "1. Start the server (in a new terminal):"
echo "   cd $TEST_DIR/server"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. Start the dashboard (optional, in another terminal):"
echo "   cd $TEST_DIR/dashboard"
echo "   npm run dev"
echo ""
echo "3. Run the demo (in another terminal):"
echo "   cd $TEST_DIR/sdk"
echo "   source ../server/venv/bin/activate  # Use server's venv"
echo "   python examples/demo_agent.py"
echo ""
echo "Test directory: $TEST_DIR"
echo ""

