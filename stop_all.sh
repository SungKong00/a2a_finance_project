#!/bin/bash
# A2A Stock Analysis System Stop Script

echo "🛑 Stopping A2A Stock Analysis System..."
echo ""

# Kill UI
echo "Stopping Demo UI..."
pkill -f "uv run main.py"
pkill -f "demo/ui/main.py"

# Kill All Agents
echo "Stopping All Analyst Agents..."
pkill -f "uvicorn agent:a2a_app"

sleep 2

# Check if stopped
echo ""
echo "Checking ports..."
if lsof -i :12000 > /dev/null 2>&1; then
    echo "❌ UI still running on port 12000"
else
    echo "✅ Demo UI stopped"
fi

if lsof -i :10101 > /dev/null 2>&1; then
    echo "❌ Technical Analyst still running on port 10101"
else
    echo "✅ Technical Analyst stopped"
fi

if lsof -i :10102 > /dev/null 2>&1; then
    echo "❌ Fundamental Analyst still running on port 10102"
else
    echo "✅ Fundamental Analyst stopped"
fi

if lsof -i :10103 > /dev/null 2>&1; then
    echo "❌ Sentiment Analyst still running on port 10103"
else
    echo "✅ Sentiment Analyst stopped"
fi

if lsof -i :10104 > /dev/null 2>&1; then
    echo "❌ Risk Assessor still running on port 10104"
else
    echo "✅ Risk Assessor stopped"
fi

echo ""
echo "✅ All services stopped!"
