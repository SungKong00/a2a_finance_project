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

# Start Technical Analyst Agent (Port 10101)
echo ""
echo "🤖 Starting Technical Analyst Agent (Port 10101)..."
cd "$PROJECT_ROOT/agents/technical_analyst"
uv run uvicorn agent:a2a_app --host 0.0.0.0 --port 10101 > /tmp/technical_analyst.log 2>&1 &
TECH_PID=$!
echo "   PID: $TECH_PID"
sleep 5

# Check if agent started successfully
if lsof -i :10101 > /dev/null 2>&1; then
    echo "   ✅ Technical Analyst Agent running"
else
    echo "   ❌ Failed to start Technical Analyst Agent"
    echo "   📄 Check logs: tail -f /tmp/technical_analyst.log"
    exit 1
fi

# Start Fundamental Analyst Agent (Port 10102)
echo ""
echo "🤖 Starting Fundamental Analyst Agent (Port 10102)..."
cd "$PROJECT_ROOT/agents/fundamental_analyst"
uv run uvicorn agent:a2a_app --host 0.0.0.0 --port 10102 > /tmp/fundamental_analyst.log 2>&1 &
FUND_PID=$!
echo "   PID: $FUND_PID"
sleep 4

# Check if agent started successfully
if lsof -i :10102 > /dev/null 2>&1; then
    echo "   ✅ Fundamental Analyst Agent running"
else
    echo "   ❌ Failed to start Fundamental Analyst Agent"
    echo "   📄 Check logs: tail -f /tmp/fundamental_analyst.log"
    exit 1
fi

# Start Sentiment Analyst Agent (Port 10103)
echo ""
echo "🤖 Starting Sentiment Analyst Agent (Port 10103)..."
cd "$PROJECT_ROOT/agents/sentiment_analyst"
uv run uvicorn agent:a2a_app --host 0.0.0.0 --port 10103 > /tmp/sentiment_analyst.log 2>&1 &
SENT_PID=$!
echo "   PID: $SENT_PID"
sleep 4

# Check if agent started successfully
if lsof -i :10103 > /dev/null 2>&1; then
    echo "   ✅ Sentiment Analyst Agent running"
else
    echo "   ❌ Failed to start Sentiment Analyst Agent"
    echo "   📄 Check logs: tail -f /tmp/sentiment_analyst.log"
    exit 1
fi

# Start Risk Assessor Agent (Port 10104)
echo ""
echo "🤖 Starting Risk Assessor Agent (Port 10104)..."
cd "$PROJECT_ROOT/agents/risk_assessor"
uv run uvicorn agent:a2a_app --host 0.0.0.0 --port 10104 > /tmp/risk_assessor.log 2>&1 &
RISK_PID=$!
echo "   PID: $RISK_PID"
sleep 4

# Check if agent started successfully
if lsof -i :10104 > /dev/null 2>&1; then
    echo "   ✅ Risk Assessor Agent running"
else
    echo "   ❌ Failed to start Risk Assessor Agent"
    echo "   📄 Check logs: tail -f /tmp/risk_assessor.log"
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
echo "===================================================================="
echo "✅ All services started successfully!"
echo "===================================================================="
echo ""
echo "📊 Access points:"
echo "   🌐 Demo UI:               http://localhost:12000"
echo "   🤖 Technical Analyst:     http://localhost:10101"
echo "   🤖 Fundamental Analyst:   http://localhost:10102"
echo "   🤖 Sentiment Analyst:     http://localhost:10103"
echo "   🤖 Risk Assessor:         http://localhost:10104"
echo ""
echo "📋 Next steps:"
echo "   1. Open http://localhost:12000 in browser"
echo "   2. Click robot icon 🤖 to add agents"
echo "   3. Add all 4 agents:"
echo "      - localhost:10101 (Technical Analyst)"
echo "      - localhost:10102 (Fundamental Analyst)"
echo "      - localhost:10103 (Sentiment Analyst)"
echo "      - localhost:10104 (Risk Assessor)"
echo "   4. Test: '삼성전자 주가 분석해줘' or 'Analyze Apple stock'"
echo ""
echo "📄 Logs:"
echo "   UI:          tail -f /tmp/demo_ui.log"
echo "   Technical:   tail -f /tmp/technical_analyst.log"
echo "   Fundamental: tail -f /tmp/fundamental_analyst.log"
echo "   Sentiment:   tail -f /tmp/sentiment_analyst.log"
echo "   Risk:        tail -f /tmp/risk_assessor.log"
echo ""
echo "🛑 To stop: ./stop_all.sh"
echo ""
