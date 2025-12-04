"""
Technical Analyst A2A Agent

A specialized agent focused on technical analysis:
- Chart patterns and trends
- Technical indicators (RSI, MACD, Moving Averages)
- Support/resistance levels
- Volume analysis
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



# Create the Technical Analyst agent
root_agent = Agent(
    name='technical_analyst',
    model=Gemini(model='gemini-2.0-flash-001', api_key=os.getenv('GOOGLE_API_KEY')),
    description='Expert technical analyst specializing in chart patterns, indicators, and price action analysis',
    instruction="""You are an expert Technical Analyst for stock markets.

    **Your Goal**: Analyze the price action, trends, and technical indicators of a given stock ticker.

    **Tools**: You have access to `yfmcp` (Yahoo Finance MCP) to fetch price history and technical data.
    - Use `get_price_history` to see trends.
    - Use `get_technical_indicators` (if available) or calculate them from price history.

    **Analysis Framework**:
    1. **Trend Analysis**: Identify the primary trend (Uptrend, Downtrend, Sideways) using Moving Averages (SMA/EMA).
    2. **Momentum**: Check RSI (Relative Strength Index) and MACD (Moving Average Convergence Divergence).
    3. **Support & Resistance**: Identify key price levels where the stock might bounce or break through.
    4. **Chart Patterns**: Look for common patterns (Head & Shoulders, Double Top/Bottom, Flags, etc.).

    **Output Format**:
    Provide a detailed technical analysis report in markdown format.
    
    **CRITICAL: You MUST end your response with a JSON block containing the following structured data:**
    ```json
    {
      "ticker": "string",
      "current_price": float,
      "trend": "Bullish" | "Bearish" | "Neutral",
      "rsi": float,
      "macd_signal": "string",
      "support_levels": [float],
      "resistance_levels": [float],
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
a2a_app = to_a2a(root_agent, port=int(os.getenv('PORT', '10101')))
