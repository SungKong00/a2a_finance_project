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
    model=Gemini(model='gemini-2.5-flash'),
    description='Expert sentiment analyst specializing in news analysis, analyst ratings, and market mood',
    instruction="""감성 분석가. 주식의 시장 심리와 뉴스를 분석합니다.

도구: get_ticker_news, get_ticker_info

**반드시 아래 JSON 형식으로만 응답. 다른 텍스트 금지:**
```json
{"ticker":"AAPL","sentiment_score":7.5,"sentiment_verdict":"강세","analyst_consensus":"매수 75%, 보유 20%, 매도 5%","top_headlines":["뉴스1","뉴스2","뉴스3"],"summary":"분석 요약"}
```

필수 필드: ticker, sentiment_score(1-10), sentiment_verdict(강세/약세/중립), analyst_consensus, top_headlines(한국어 3개), summary(한국어)
""",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='uvx',
                    args=['yfmcp@latest'],
                ),
                timeout_seconds=60,  # Increase timeout for Yahoo Finance API calls
            ),
        )
    ],
)



# Convert ADK agent to A2A server
a2a_app = to_a2a(root_agent, port=int(os.getenv('PORT', '10103')))
