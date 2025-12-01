# 🛠️ System Design: Demo + MCP Integration

This document details the **technical implementation** of integrating a new MCP Server into the existing A2A Demo codebase with minimal modifications.

## 1. Workspace Structure (Monorepo)

We use `uv` workspaces to manage dependencies for multiple components in a single repository.

```text
my-a2a-project/
├── pyproject.toml              # Workspace Root (Defines members)
├── .env                        # API Keys (GOOGLE_API_KEY, MCP_URL)
├── demo/
│   └── ui/                     # Copied from a2a-samples-main/demo/ui
│       └── ... (Mesop UI)
├── hosts/
│   └── multiagent/             # Copied from a2a-samples-main/samples/python/hosts/multiagent
│       ├── host_agent.py       # [MODIFIED] To support MCP Client
│       └── ...
├── extensions/
│   └── timestamp/              # Copied dependency
├── mcp_server/                 # [NEW] Local Tool Server
│   ├── pyproject.toml
│   └── server.py               # yfinance logic
└── docs/
    ├── AGENT_ARCHITECTURE.md   # Business Logic
    └── SYSTEM_DESIGN.md        # This File
```

## 2. Technical Implementation Steps

### Step A: MCP Server (`mcp_server/`)
A standalone Python process running the Model Context Protocol.

*   **Dependencies:** `mcp`, `yfinance`, `pandas`.
*   **Transport:** Stdio (Standard Input/Output) or SSE (Server-Sent Events). *We will use SSE for easier debugging with the Host Agent.*
*   **Key Functions:**
    *   `get_ticker(query: str) -> str`: Uses `yfinance` search to find the best match symbol.
    *   `get_stock_data(ticker: str) -> dict`: Returns a JSON object with Price, PER, VIX, Target Price, etc.

### Step B: Host Agent Modification (`hosts/multiagent/`)
The Host Agent needs to "know" about the MCP server.

*   **File:** `hosts/multiagent/host_agent.py`
*   **Change 1: Initialization:**
    *   Add an `mcp_client` instance to the `HostAgent` class.
    *   Connect to `http://localhost:10100` (MCP SSE endpoint) on startup.
*   **Change 2: Tool Registration:**
    *   Fetch available tools from MCP (`ListTools`).
    *   Convert them to `google.genai.types.FunctionDeclaration` format.
    *   Pass these tools to the Gemini model initialization.
*   **Change 3: Execution Loop:**
    *   When Gemini returns a `FunctionCall` for an MCP tool:
        *   Intercept it.
        *   Execute it via the `mcp_client`.
        *   Feed the result back to Gemini.

### Step C: UI Integration (`demo/ui/`)
The UI needs to connect to the modified Host Agent.

*   **File:** `demo/ui/service/server/adk_host_manager.py`
*   **Change:** When initializing `HostAgent`, pass the `MCP_SERVER_URL` from the environment variables.

## 3. Execution Flow

1.  **Start MCP Server:** Run `python -m mcp_server.server` (listens on port 10100).
2.  **Start Remote Agent:** Run the Stock Analyst Agent (listens on port 10101).
3.  **Start UI & Host:** Run `python demo/ui/main.py` (listens on port 12000).
    *   Host Agent connects to MCP (10100).
    *   Host Agent connects to Remote Agent (10101).
4.  **User Interaction:** User accesses `http://localhost:12000`.

## 4. Dependency Management (`pyproject.toml`)

The root `pyproject.toml` allows all sub-projects to share the same virtual environment, reducing disk space and conflict.

```toml
[tool.uv.workspace]
members = [
    "demo/ui",
    "hosts/multiagent",
    "mcp_server",
    "extensions/*"
]
```

## 5. "Minimal Modification" Strategy

To keep the project stable and easy to diff against the original demo:

1.  **Keep Original Files:** Do not delete or rename original files unless necessary.
2.  **Extension over Modification:** Add new logic in new methods or classes where possible.
3.  **Config over Code:** Use `.env` for URLs and Keys instead of hardcoding.
