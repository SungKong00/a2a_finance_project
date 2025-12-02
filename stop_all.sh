#!/bin/bash
# A2A Stock Analysis System Stop Script

echo "🛑 Stopping A2A Stock Analysis System..."
echo ""

# Kill UI
echo "Stopping Demo UI..."
pkill -f "uv run main.py"
pkill -f "demo/ui/main.py"

# Kill Agent
echo "Stopping Stock Analyst Agent..."
pkill -f "uvicorn agent:a2a_app"

sleep 2

# Check if stopped
if lsof -i :12000 > /dev/null 2>&1; then
    echo "❌ UI still running on port 12000"
else
    echo "✅ Demo UI stopped"
fi

if lsof -i :10101 > /dev/null 2>&1; then
    echo "❌ Agent still running on port 10101"
else
    echo "✅ Stock Analyst Agent stopped"
fi

echo ""
echo "Done!"
