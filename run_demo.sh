#!/bin/bash
# SudoMode Demo Runner
# Quick script to help users run the demo

set -e

echo "🛡️  SudoMode Demo Runner"
echo "========================"
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Warning: Server doesn't appear to be running on http://localhost:8000"
    echo ""
    echo "Please start the server first:"
    echo "  cd server"
    echo "  source venv/bin/activate  # or: venv\\Scripts\\activate (Windows)"
    echo "  uvicorn app.main:app --reload"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to cancel..."
    echo ""
fi

# Navigate to SDK directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/sdk"

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "💡 Tip: Consider activating a virtual environment first"
    echo "   source ../server/venv/bin/activate"
    echo ""
fi

# Check if dependencies are installed
if ! python -c "import httpx" 2>/dev/null; then
    echo "📦 Installing SDK dependencies..."
    pip install -r requirements.txt --quiet
fi

# Run the demo
echo "🚀 Running SudoMode demo..."
echo ""
python examples/demo_agent.py
