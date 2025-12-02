#!/bin/bash
# A2A Stock Analysis System Startup Script

echo "🚀 Starting A2A Stock Analysis System..."
echo ""

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    if [ -f "demo/ui/.env" ]; then
        export $(cat demo/ui/.env | grep -v '^#' | xargs)
        echo "✅ Loaded API key from demo/ui/.env"
    else
        echo "❌ Error: GOOGLE_API_KEY not found!"
        echo "   Please create demo/ui/.env with: GOOGLE_API_KEY=your_key_here"
        exit 1
    fi
fi

# Kill existing processes
echo ""
echo "🧹 Cleaning up existing processes..."
pkill -f "uv run main.py" 2>/dev/null
pkill -f "uvicorn agent:a2a_app" 2>/dev/null
sleep 2

# Start Stock Analyst Agent (Port 10101)
echo ""
echo "🤖 Starting Stock Analyst Agent (Port 10101)..."
cd "$PROJECT_ROOT/agents/stock_analyst"
uv run uvicorn agent:a2a_app --host 0.0.0.0 --port 10101 > /tmp/stock_analyst.log 2>&1 &
AGENT_PID=$!
echo "   PID: $AGENT_PID"
sleep 3

# Check if agent started successfully
if lsof -i :10101 > /dev/null 2>&1; then
    echo "   ✅ Stock Analyst Agent running"
else
    echo "   ❌ Failed to start Stock Analyst Agent"
    echo "   📄 Check logs: tail -f /tmp/stock_analyst.log"
    exit 1
fi

# Start Demo UI (Port 12000)
echo ""
echo "🌐 Starting Demo UI (Port 12000)..."
cd "$PROJECT_ROOT/demo/ui"
uv run main.py > /tmp/demo_ui.log 2>&1 &
UI_PID=$!
echo "   PID: $UI_PID"
sleep 5

# Check if UI started successfully
if lsof -i :12000 > /dev/null 2>&1; then
    echo "   ✅ Demo UI running"
else
    echo "   ❌ Failed to start Demo UI"
    echo "   📄 Check logs: tail -f /tmp/demo_ui.log"
    exit 1
fi

echo ""
echo "================================================"
echo "✅ All services started successfully!"
echo "================================================"
echo ""
echo "📊 Access points:"
echo "   🌐 Demo UI:          http://localhost:12000"
echo "   🤖 Stock Analyst:    http://localhost:10101"
echo ""
echo "📋 Next steps:"
echo "   1. Open http://localhost:12000 in browser"
echo "   2. Click robot icon to add agent"
echo "   3. Enter: localhost:10101"
echo "   4. Test: '삼성전자 주가 분석해줘'"
echo ""
echo "📄 Logs:"
echo "   UI:    tail -f /tmp/demo_ui.log"
echo "   Agent: tail -f /tmp/stock_analyst.log"
echo ""
echo "🛑 To stop: ./stop_all.sh"
echo ""
