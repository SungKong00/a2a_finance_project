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
    model=Gemini(model='gemini-2.5-flash-lite'),
    description='Expert technical analyst specializing in chart patterns, indicators, and price action analysis',
    instruction="""기술적 분석가. 주식의 추세와 기술 지표를 분석합니다.

도구: get_price_history(period=1mo), get_ticker_info

**반드시 아래 JSON 형식으로만 응답. 다른 텍스트 금지:**
```json
{"ticker":"AAPL","current_price":178.5,"trend":"강세","rsi":62.5,"macd_signal":"골든크로스","support_levels":[170,165],"resistance_levels":[185,190],"summary":"분석 요약"}
```

필수 필드: ticker, current_price, trend(강세/약세/중립), rsi(0-100), macd_signal, support_levels, resistance_levels, summary(한국어)
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
a2a_app = to_a2a(root_agent, port=int(os.getenv('PORT', '10101')))
