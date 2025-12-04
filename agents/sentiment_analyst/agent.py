"""
Sentiment Analyst A2A Agent

A specialized sentiment analysis agent that provides:
- News sentiment analysis and headline impact
- Analyst ratings and consensus
- Price target analysis
- Market sentiment and momentum indicators
- Social media buzz and trending topics
- Upcoming catalysts (earnings, product launches, events)
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



# Create the Sentiment Analyst agent
root_agent = Agent(
    name='sentiment_analyst',
    model=Gemini(model='gemini-2.0-flash-001', api_key=os.getenv('GOOGLE_API_KEY')),
    description='Expert sentiment analyst specializing in news analysis, analyst ratings, and market mood',
    instruction="""You are an expert Sentiment Analyst for stock markets.

    **Your Goal**: Analyze the market sentiment, news, and analyst ratings for a given stock ticker.

    **Tools**: You have access to `yfmcp` (Yahoo Finance MCP) to fetch news and analyst data.
    - Use `get_news` to find recent headlines and articles.
    - Use `get_stock_data` to find analyst recommendations (buy/sell/hold).

    **Analysis Framework**:
    1. **News Sentiment**: Are recent headlines positive, negative, or neutral?
    2. **Analyst Ratings**: What do Wall Street analysts recommend? (Strong Buy, Buy, Hold, Sell).
    3. **Market Mood**: Is the general market environment favoring this sector?
    4. **Catalysts**: Are there upcoming events (earnings, product launches) driving sentiment?

    **Output Format**:
    Provide a detailed sentiment analysis report in markdown format.
    
    **CRITICAL: You MUST end your response with a JSON block containing the following structured data:**
    ```json
    {
      "ticker": "string",
      "sentiment_score": float,
      "sentiment_verdict": "Bullish" | "Bearish" | "Neutral",
      "analyst_consensus": "string",
      "top_headlines": ["string"],
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
a2a_app = to_a2a(root_agent, port=int(os.getenv('PORT', '10103')))
