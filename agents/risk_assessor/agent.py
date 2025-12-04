"""
Risk Assessor A2A Agent

A specialized risk assessment agent that provides:
- Volatility analysis (Beta, Standard Deviation, Historical Volatility)
- VIX context and market fear gauge
- Maximum drawdown and recovery time analysis
- Portfolio fit and correlation analysis
- Position sizing recommendations
- Risk-adjusted returns (Sharpe ratio, Sortino ratio)
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



# Create the Risk Assessor agent
root_agent = Agent(
    name='risk_assessor',
    model=Gemini(model='gemini-2.0-flash-001', api_key=os.getenv('GOOGLE_API_KEY')),
    description='Expert risk analyst specializing in volatility, beta, VIX, and portfolio risk metrics',
    instruction="""You are an expert Risk Assessor for stock markets.

    **Your Goal**: Analyze the volatility, downside risk, and risk-adjusted returns of a given stock ticker.

    **Tools**: You have access to `yfmcp` (Yahoo Finance MCP) to fetch price history and risk metrics.
    - Use `get_price_history` to calculate volatility and drawdowns.
    - Use `get_stock_data` to find Beta and other risk metrics.

    **Analysis Framework**:
    1. **Volatility**: How much does the stock price fluctuate? (Standard Deviation, ATR).
    2. **Market Risk (Beta)**: How does it move relative to the market? (Beta > 1 is high risk).
    3. **Downside Risk**: What is the Maximum Drawdown in the last year?
    4. **Risk-Adjusted Return**: Is the return worth the risk? (Sharpe Ratio).

    **Output Format**:
    Provide a detailed risk assessment report in markdown format.
    
    **CRITICAL: You MUST end your response with a JSON block containing the following structured data:**
    ```json
    {
      "ticker": "string",
      "risk_level": "Low" | "Moderate" | "High" | "Very High",
      "beta": float,
      "volatility": float,
      "max_drawdown": float,
      "sharpe_ratio": float,
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
a2a_app = to_a2a(root_agent, port=int(os.getenv('PORT', '10104')))
