# 🛠️ System Design: Demo + MCP Integration

This document details the **technical implementation** of integrating **existing MCP Servers** (like yfinance-mcp) into the A2A Demo codebase with minimal modifications.

## 1. Workspace Structure (Monorepo)

We use `uv` workspaces to manage dependencies for multiple components in a single repository.

```text
my-a2a-project/
├── pyproject.toml              # Workspace Root (Defines members)
├── .env                        # API Keys (GOOGLE_API_KEY, MCP_SERVER_URL)
├── demo/
│   └── ui/                     # Copied from a2a-samples-main/demo/ui
│       └── ... (Mesop UI)
├── hosts/
│   └── multiagent/             # Copied from a2a-samples-main/samples/python/hosts/multiagent
│       ├── host_agent.py       # [MODIFIED] To connect to external MCP servers
│       └── ...
├── agents/
│   └── stock_analyst/          # [NEW] A2A Remote Agent for stock analysis
│       ├── agent.py
│       └── pyproject.toml
├── extensions/
│   └── timestamp/              # Copied dependency
└── docs/
    ├── AGENT_ARCHITECTURE.md   # Business Logic
    └── SYSTEM_DESIGN.md        # This File
```

**Note:** We do NOT create a custom MCP server. Instead, we use existing open-source MCP servers (e.g., `yfmcp`, `yahoo-finance-mcp`).

## 2. Technical Implementation Steps

### Step A: Use Existing MCP Server (External Tool)

We leverage **existing open-source MCP servers** instead of building our own. This follows the same pattern as using Playwright MCP.

#### **Recommended MCP Servers for Stock Data:**

1. **yfmcp (narumiruna/yfinance-mcp)** - Simple and popular
   - GitHub: https://github.com/narumiruna/yfinance-mcp
   - Installation: `uvx yfmcp --port 10100`

2. **yahoo-finance-mcp (Alex2Yang97)** - Most comprehensive
   - GitHub: https://github.com/Alex2Yang97/yahoo-finance-mcp
   - Features: Historical data, financials, options, news

3. **9nate-drake/mcp-yfinance** - Claude Desktop optimized
   - GitHub: https://github.com/9nate-drake/mcp-yfinance

#### **How to Run:**
```bash
# Option 1: Using uvx (recommended)
uvx yfmcp --port 10100

# Option 2: Using npx (if Node.js version exists)
npx @your-package/yahoo-finance-mcp --port 10100
```

The MCP server will expose an SSE endpoint at `http://localhost:10100/sse`.

#### **Available Tools (Example from yfmcp):**
- `get_stock_info(ticker)`: Company info, market cap, financials
- `get_historical_data(ticker, period, interval)`: Price history
- `get_analyst_recommendations(ticker)`: Buy/Sell ratings
- `get_news(ticker)`: Recent news articles

---

### Step B: Host Agent Modification (`hosts/multiagent/`)

The Host Agent orchestrates multiple specialized A2A agents. MCP server provides data that agents use in their analysis.

#### **File:** `hosts/multiagent/host_agent.py`

#### **Minimal Changes Required:**

**Change 1: Enhanced Instruction for Multi-Agent Coordination**
```python
def root_instruction(self, context: ReadonlyContext) -> str:
    current_agent = self.check_state(context)
    return f"""You are an expert financial analyst coordinating specialized stock analysis agents.

WORKFLOW FOR STOCK ANALYSIS:
1. Parse stock ticker from user request (e.g., "AAPL", "TSLA", "MSFT")
2. Delegate analysis to specialized agents in parallel:
   - Technical Analyst: Chart patterns, indicators (RSI, MACD, Moving Averages)
   - Fundamental Analyst: Earnings, PE ratio, revenue growth, margins
   - Sentiment Analyst: News headlines, market sentiment, analyst ratings
   - Risk Assessor: Volatility (VIX), beta, drawdown risk

3. Collect all agent responses
4. Synthesize findings into comprehensive investment report

Available Specialized Agents:
{self.agents}

Current Active Agent: {current_agent['active_agent']}
"""
```

**That's it!** The existing HostAgent delegation mechanism handles everything else.

---

### Step C: Create Specialized A2A Remote Agents (`agents/`)

We create **4 specialized A2A agents** for comprehensive stock analysis (NOT MCP servers).

#### **1. Technical Analyst** (`agents/technical_analyst/agent.py`) - Port 10101
- Chart patterns, indicators (RSI, MACD, Moving Averages)
- Support/resistance levels, trend analysis

#### **2. Fundamental Analyst** (`agents/fundamental_analyst/agent.py`) - Port 10102
- Earnings, PE ratio, revenue growth, financial health
- Valuation metrics (P/E, P/B, PEG, ROE)

#### **3. Sentiment Analyst** (`agents/sentiment_analyst/agent.py`) - Port 10103
- News headlines, market sentiment, analyst ratings
- Social media buzz, upcoming catalysts

#### **4. Risk Assessor** (`agents/risk_assessor/agent.py`) - Port 10104
- Volatility (VIX), beta, maximum drawdown
- Portfolio fit, risk-adjusted recommendations

**Each agent follows the same structure:**
```python
from google.adk import Agent
from google.adk.a2a import A2aServer
from google.adk.models.lite_llm import LiteLlm

def create_[specialist]_agent():
    return Agent(
        model=LiteLlm(model='gemini/gemini-2.0-flash-001'),
        name='[Specialist Name]',
        description='Expert in [domain]',
        instruction="""[Detailed analysis framework and output format]"""
    )

if __name__ == '__main__':
    agent = create_[specialist]_agent()
    server = A2aServer(agent)
    server.run(port=[10101-10104])
```

**Note:** Each agent is an independent A2A server, not an MCP server. They receive analysis requests via A2A protocol and return structured insights.

---

### Step D: UI Integration with Auto-Registration

The UI (`demo/ui/`) requires **minimal modification** for automatic agent registration.

#### **File:** `demo/ui/service/server/adk_host_manager.py`

**Change:** Load agents from JSON configuration file instead of empty list.

**Current (Line 66):**
```python
self._host_agent = HostAgent([], http_client, self.task_callback)
```

**Modified:**
```python
# Load pre-configured agents from JSON
initial_agents = self._load_agent_config()
self._host_agent = HostAgent(initial_agents, http_client, self.task_callback)
```

**Add method (after Line 85):**
```python
def _load_agent_config(self) -> list[str]:
    """Load agent addresses from configuration file."""
    config_path = os.environ.get('AGENT_CONFIG_PATH', './agents.json')

    if not os.path.exists(config_path):
        return []

    with open(config_path, 'r') as f:
        config = json.load(f)

    agents = config.get('agents', [])
    return [agent['address'] for agent in agents if agent.get('auto_start', True)]
```

This enables automatic agent registration on startup without manual UI interaction.

## 3. Execution Flow

### **Step-by-Step Startup Process:**

```bash
# Terminal 1: Start External MCP Server (yfinance tools)
uvx yfmcp --port 10100
# Output: MCP server running at http://localhost:10100/sse

# Terminal 2-5: Start 4 Specialized A2A Agents
cd agents/technical_analyst && uv run agent.py    # Port 10101
cd agents/fundamental_analyst && uv run agent.py  # Port 10102
cd agents/sentiment_analyst && uv run agent.py    # Port 10103
cd agents/risk_assessor && uv run agent.py        # Port 10104

# Terminal 6: Start UI + Host Agent
cd demo/ui
uv run main.py
# Output: Mesop UI running at http://localhost:12000
#         Auto-registering 4 agents: ['localhost:10101', 'localhost:10102', ...]

# Or use the startup script:
./run_all.sh
```

### **Data Flow During User Request:**

1. **User Input:** User asks "Should I invest in Apple stock?" via UI (`http://localhost:12000`)

2. **Host Agent Processing:**
   - Receives user request
   - Identifies ticker: AAPL
   - Decides to delegate to all 4 specialized agents

3. **Parallel A2A Delegation:**
   - **Technical Analyst (10101):** Analyzes price trends, RSI, MACD → Returns technical outlook
   - **Fundamental Analyst (10102):** Reviews P/E, earnings, growth → Returns valuation assessment
   - **Sentiment Analyst (10103):** Checks news, analyst ratings → Returns sentiment analysis
   - **Risk Assessor (10104):** Evaluates volatility, beta → Returns risk evaluation

4. **Synthesis:** Host Agent combines all 4 reports into comprehensive recommendation

5. **Response:** User sees unified report with:
   - Technical outlook (bullish/bearish)
   - Valuation (undervalued/overvalued)
   - Sentiment (positive/negative)
   - Risk level (low/moderate/high)
   - Final recommendation (BUY/HOLD/SELL)

### **Architecture Diagram:**

```
┌─────────────────┐
│   User UI       │ (Port 12000)
│   (Mesop)       │
└────────┬────────┘
         │
         v
┌────────────────────────────────────┐
│      Host Agent (ADK)              │
│      - Orchestrator                │
│      - Auto-registered agents      │
└──┬──┬──┬──┬─────────────────────┬──┘
   │  │  │  │                     │
   │  │  │  │                     │ (Data source for agents)
   │  │  │  │                     v
   │  │  │  │              ┌──────────────┐
   │  │  │  │              │ yfmcp MCP    │
   │  │  │  │              │ :10100       │
   │  │  │  │              └──────────────┘
   │  │  │  │
   │  │  │  └─→ Technical Analyst (A2A :10101)
   │  │  └────→ Fundamental Analyst (A2A :10102)
   │  └───────→ Sentiment Analyst (A2A :10103)
   └──────────→ Risk Assessor (A2A :10104)
```

---

## 4. Dependency Management (`pyproject.toml`)

The root `pyproject.toml` defines a monorepo workspace for all components.

```toml
[tool.uv.workspace]
members = [
    "demo/ui",
    "hosts/multiagent",
    "agents/*",          # A2A Remote Agents
    "extensions/*"       # Timestamp and other extensions
]

[project]
name = "my-a2a-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []  # Shared dependencies (if any)
```

**Note:** Each workspace member has its own `pyproject.toml` with specific dependencies.

---

## 5. Environment Variables (`.env`)

```bash
# Google AI API Key (required)
GOOGLE_API_KEY=your_api_key_here

# Or use Vertex AI (alternative)
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_CLOUD_PROJECT=your_project_id
# GOOGLE_CLOUD_LOCATION=us-central1

# MCP Server URL (optional, defaults to localhost:10100)
MCP_SERVER_URL=http://localhost:10100/sse

# LiteLLM Model (optional)
LITELLM_MODEL=gemini/gemini-2.0-flash-001

# UI Server Settings (optional)
A2A_UI_HOST=0.0.0.0
A2A_UI_PORT=12000
```

---

## 6. "Minimal Modification" Strategy

To keep the project maintainable and aligned with the original demo:

### **Principles:**

1. **Use Existing MCP Servers:** Never reinvent the wheel. Leverage open-source MCP tools.

2. **Keep Demo UI Unchanged:** The UI from `a2a-samples-main/demo/ui` is copied as-is.

3. **Minimal Host Agent Changes:** Only add MCP connection logic (~15 lines of code).

4. **Config over Code:** Use `.env` for all URLs, API keys, and ports.

5. **Workspace Structure:** Follow the same pattern as `a2a-samples-main`.

### **Files Modified:**
- ✅ `hosts/multiagent/host_agent.py` - Add MCP toolset connection
- ✅ `.env` - Add `MCP_SERVER_URL`
- ❌ `demo/ui/*` - No changes needed

### **Files Added:**
- ✅ `agents/stock_analyst/agent.py` - A2A remote agent
- ✅ `pyproject.toml` - Workspace root
- ✅ `docs/*` - Architecture and design docs

---

## 7. Testing the Integration

### **Verification Steps:**

1. **Test MCP Server:**
   ```bash
   # Check if MCP server is running
   curl http://localhost:10100/sse
   ```

2. **Test A2A Remote Agent:**
   ```bash
   # Check if agent card is accessible
   curl http://localhost:10101/.well-known/agent.json
   ```

3. **Test Host Agent:**
   - Open `http://localhost:12000`
   - Go to "Remote Agents" tab
   - Add agent: `localhost:10101`
   - Ask: "What remote agents do you have?"

4. **Test Full Flow:**
   - Ask: "Get current price of Apple stock"
   - Host should use MCP tool `get_stock_info("AAPL")`
   - Then ask: "Should I invest in Apple?"
   - Host should delegate to Stock Analyst agent

---

## 8. Troubleshooting

### **Common Issues:**

**MCP Server Not Found:**
```
Error: Cannot connect to http://localhost:10100/sse
Solution: Ensure MCP server is running in a separate terminal
```

**A2A Agent Not Registered:**
```
Error: Agent 'Stock Analyst' not found
Solution: Manually add agent in UI or check port 10101
```

**API Key Issues:**
```
Error: GOOGLE_API_KEY not set
Solution: Create .env file with valid API key
```

---

## 9. Next Steps (Future Enhancements)

### **Phase 1: MVP** ✅
- [x] Connect to external MCP server (yfmcp)
- [x] Create Stock Analyst A2A agent
- [x] Integrate with demo UI

### **Phase 2: Advanced Features**
- [ ] Add multiple MCP servers (news, technical analysis)
- [ ] Implement peer comparison agent
- [ ] Add chart visualization

### **Phase 3: Production**
- [ ] Deploy to Cloud Run
- [ ] Add authentication
- [ ] Implement rate limiting
