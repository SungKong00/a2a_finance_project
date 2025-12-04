"""
Fundamental Analyst A2A Agent

A specialized fundamental analysis agent that provides:
- Financial statement analysis (Income Statement, Balance Sheet, Cash Flow)
- Valuation metrics (P/E, P/B, PEG, EV/EBITDA, DCF)
- Earnings and revenue growth analysis
- Profitability metrics (ROE, ROA, Margins)
- Competitive positioning and industry analysis
"""

import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models import Gemini
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Load environment variables
load_dotenv()



# Create the Fundamental Analyst agent
root_agent = Agent(
    name='fundamental_analyst',
    model=Gemini(model='gemini-2.0-flash-001', api_key=os.getenv('GOOGLE_API_KEY')),
    description='Expert fundamental analyst specializing in financial statements, valuation metrics, and company analysis',
    instruction="""You are an expert Fundamental Analyst for stock markets.

    **Your Goal**: Analyze the financial health, valuation, and growth prospects of a given stock ticker.

    **Tools**: You have access to `yfmcp` (Yahoo Finance MCP) to fetch financial data.
    - Use `get_stock_data` to find P/E ratio, market cap, financial metrics.
    - Use `get_financial_statements` to analyze income statement, balance sheet, cash flow.

    **Analysis Framework**:
    1. **Valuation**: Is the stock overvalued or undervalued? (P/E, P/B, PEG ratios).
    2. **Financial Health**: Strong balance sheet? (Debt-to-Equity, Current Ratio, Cash reserves).
    3. **Growth**: Revenue and earnings growth trends (YoY, QoQ).
    4. **Profitability**: ROE, ROA, Operating Margin, Net Margin.

    **Output Format**:
    Provide a detailed fundamental analysis report in markdown format.

    **CRITICAL: You MUST end your response with a JSON block containing the following structured data:**
    ```json
    {
      "ticker": "string",
      "valuation": "Undervalued" | "Fairly Valued" | "Overvalued",
      "pe_ratio": float,
      "revenue_growth_yoy": float,
      "roe": float,
      "debt_to_equity": float,
      "recommendation": "Strong Buy" | "Buy" | "Hold" | "Sell" | "Strong Sell",
      "analysis_content": "string (Your full markdown analysis report goes here)"
    }
    ```
    Ensure the `analysis_content` field contains the complete text of your analysis.
    """,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='uvx',
                    args=['yfmcp@latest'],
                ),
                timeout_seconds=30,  # Increase timeout for Yahoo Finance API calls
            ),
        )
    ],
)

# Convert ADK agent to A2A server
a2a_app = to_a2a(root_agent, port=int(os.getenv('PORT', '10102')))
