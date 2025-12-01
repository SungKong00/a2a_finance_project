# 🏛️ AI Stock Analysis Agent Architecture

This document outlines the business logic, agent roles, and data flow for the Stock Analysis Agent. It combines **A2A (Agent-to-Agent)** for expert reasoning and **MCP (Model Context Protocol)** for real-time data fetching.

## 1. Project Overview
*   **Goal:** Automate the process of gathering scattered stock data, comparing it with peers, and generating a comprehensive investment report.
*   **Key Value Proposition:**
    *   **Automation:** Fetches financials, news, and competitor data in one go.
    *   **Insight:** Provides judgments based on market sentiment (VIX) and analyst consensus, not just raw numbers.
    *   **Scalability:** Designed to easily add technical analysis (RSI) later.

## 2. High-Level Architecture (3-Tier)

```mermaid
graph TD
    User[User UI (Input Ticker)] --> Host[Host Agent (Orchestrator)]
    
    subgraph "Tier 1: Execution (MCP Server)"
        Host -->|Tools Call| MCP[MCP Server (Local Tools)]
        MCP -->|yfinance| MarketData[Stock/Market Data]
    end
    
    subgraph "Tier 2: Intelligence (Remote A2A)"
        Host -->|Raw Data| Analyst[Remote Agent (Stock Analyst)]
        Analyst -->|Analysis Report| Host
    end
    
    Host -->|Final Output| User
```

## 3. Agent Roles & Responsibilities

### A. Host Agent (The Project Manager)
*   **Role:** Orchestrates the entire workflow. Doesn't do the heavy lifting but knows who to ask.
*   **Algorithm:**
    1.  Receives user input (Stock Name).
    2.  Asks **MCP** to find the ticker symbol and fetch data.
    3.  Aggregates the data and sends it to the **Remote Agent**.
    4.  Delivers the final report to the user.

### B. MCP Server (The Data Fetcher)
*   **Technology:** Python `mcp` SDK + `yfinance`.
*   **Tools (MVP):**
    1.  `get_ticker(query)`: Converts name to ticker (e.g., "Apple" -> "AAPL").
    2.  `get_stock_data(ticker)`: Fetches a standardized data packet.
        *   **Fundamentals:** Price, PER, PBR, ROE.
        *   **Market Sentiment:** VIX Index (Market Fear), Sector Avg PER.
        *   **Consensus:** Analyst Target Price, Recommendation (Buy/Sell).
        *   **News:** Top 3-5 recent news headlines.

### C. Remote Agent (The Chief Analyst)
*   **Persona:** "A sharp Wall Street Fund Manager."
*   **Role:** Interprets the raw JSON data into a human-readable report.
*   **Analysis Logic:**
    *   **Valuation:** "PER is lower than the sector average, indicating undervaluation."
    *   **Sentiment:** "Target price is 20% higher than current, suggesting upside potential."
    *   **Macro:** "However, the high VIX index suggests caution due to market volatility."

## 4. Data Flow Scenario

**User Input:** "Analyze Samsung Electronics"

1.  **[Host]** Calls MCP: `get_ticker("Samsung Electronics")` -> Returns `005930.KS`
2.  **[Host]** Calls MCP: `get_stock_data("005930.KS")`
    *   *Returns:* `{ Price: 70000, PER: 10, VIX: 15, Target: 90000, News: [...] }`
3.  **[Host]** Calls Remote Agent: Sends the above JSON with instructions.
4.  **[Remote]** Generates Report: "Samsung Electronics is currently undervalued..."
5.  **[UI]** Displays the report.

## 5. Development Roadmap

### Phase 1: MVP (Core Features)
*   [ ] Setup `uv` workspace and migrate Demo code.
*   [ ] Implement MCP Server (`yfinance`: Basic stats + VIX + Target Price).
*   [ ] Modify Host Agent to connect with MCP.
*   [ ] Add simple input form to UI.

### Phase 2: Intelligence (Enhancement)
*   [ ] Tune Remote Agent prompts for better "expert" persona.
*   [ ] Automate peer group comparison.

### Phase 3: Advanced (Future)
*   [ ] **Technical Analysis:** Add RSI, Moving Averages.
*   [ ] **Deep News Analysis:** Analyze full news articles for sentiment scoring.
