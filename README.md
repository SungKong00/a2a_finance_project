# 🤖 A2A Stock Analysis Multi-Agent System

A comprehensive stock analysis system using Google's Agent-to-Agent (A2A) protocol with specialized AI agents.

## 📋 Overview

This project demonstrates a multi-agent architecture for stock analysis using:
- **A2A Protocol**: Agent-to-agent communication
- **Google ADK**: Agent Development Kit
- **Mesop**: Web UI framework
- **Gemini 2.0**: Advanced AI model

## 🏗️ Architecture

```
User → Demo UI (Mesop) → Host Agent (ADK)
                            ↓
                    Stock Analyst Agent (A2A)
                    └─ Technical Analysis
                    └─ Fundamental Analysis
                    └─ Sentiment Analysis
                    └─ Risk Assessment
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- UV package manager
- Google API Key (from [Google AI Studio](https://aistudio.google.com/app/apikey))

### 1. Setup Environment

```bash
# Create .env file with your API key
echo "GOOGLE_API_KEY=your_api_key_here" > demo/ui/.env
```

### 2. Run All Services

```bash
./run_all.sh
```

This will start:
- Demo UI at http://localhost:12000
- Stock Analyst Agent at http://localhost:10101

### 3. Register Agent in UI

1. Open http://localhost:12000
2. Click the robot icon 🤖
3. Enter agent address: `localhost:10101`
4. Agent card will be automatically loaded

### 4. Test the System

Try asking:
- "삼성전자 주가 분석해줘"
- "Should I invest in Apple stock?"
- "Analyze Tesla stock"

## 🛑 Stop Services

```bash
./stop_all.sh
```

## 📁 Project Structure

```
my-a2a-project/
├── agents/
│   └── stock_analyst/        # Stock Analyst A2A Agent
│       ├── agent.py          # Agent implementation
│       └── pyproject.toml    # Dependencies
├── demo/
│   └── ui/                   # Mesop web interface
├── hosts/
│   └── multiagent/           # Host agent (orchestrator)
├── extensions/
│   └── timestamp/            # Timestamp extension
├── docs/
│   ├── AGENT_ARCHITECTURE.md # Business logic & workflow
│   └── SYSTEM_DESIGN.md      # Technical implementation
├── run_all.sh                # Start all services
├── stop_all.sh               # Stop all services
└── pyproject.toml            # Workspace configuration
```

## 🔧 Manual Execution (Alternative)

If you prefer to run services manually:

### Terminal 1: Demo UI
```bash
cd demo/ui
uv run main.py
```

### Terminal 2: Stock Analyst Agent
```bash
cd agents/stock_analyst
uv run uvicorn agent:a2a_app --host 0.0.0.0 --port 10101
```

## 📊 Agent Features

The Stock Analyst Agent provides:

- **Technical Analysis**: Chart patterns, RSI, MACD, Moving Averages
- **Fundamental Analysis**: P/E ratios, earnings, revenue growth
- **Sentiment Analysis**: News, analyst ratings, market sentiment
- **Risk Assessment**: Volatility, beta, VIX context

## 📝 Logs

View service logs:

```bash
# UI logs
tail -f /tmp/demo_ui.log

# Agent logs
tail -f /tmp/stock_analyst.log
```

## 🔍 Verify Services

Check if services are running:

```bash
lsof -i :12000  # Demo UI
lsof -i :10101  # Stock Analyst Agent
```

Check Agent Card:

```bash
curl http://localhost:10101/.well-known/agent-card.json
```

## 📚 Documentation

- [Agent Architecture](docs/AGENT_ARCHITECTURE.md) - Business logic and workflow
- [System Design](docs/SYSTEM_DESIGN.md) - Technical implementation details
- [Google A2A Protocol](https://google.github.io/A2A/)
- [Google ADK Docs](https://google.github.io/adk-docs/)

## 🐛 Troubleshooting

### Agent not loading in UI
- Check agent is running: `lsof -i :10101`
- Verify agent card: `curl http://localhost:10101/.well-known/agent-card.json`
- Check logs: `tail -f /tmp/stock_analyst.log`

### API Key issues
- Ensure `.env` file exists in `demo/ui/`
- Verify key format: `GOOGLE_API_KEY=your_key_here`
- Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Port already in use
```bash
# Kill existing processes
./stop_all.sh

# Or manually
pkill -f "uv run main.py"
pkill -f "uvicorn agent:a2a_app"
```

## 🎯 Next Steps

- [ ] Add more specialized agents (Technical, Fundamental, Sentiment, Risk)
- [ ] Integrate MCP server for real-time stock data
- [ ] Implement agent auto-registration
- [ ] Add multi-agent coordination

## 📄 License

This project is for educational purposes.

## 🤝 Contributing

This is a university project. For questions or issues, please contact the project maintainer.
