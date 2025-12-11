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

도구 사용 규칙:
1. 단기 분석 (1개월 이내): `get_historical_data(ticker, period='1mo', interval='1d')` 사용
2. 중장기 분석 (6개월 ~ 1년): `get_historical_data(ticker, period='1y', interval='1wk')` 사용 (토큰 절약 및 효율성 증대)

**주의**: 필요 이상으로 긴 기간의 일봉(`interval='1d'`) 데이터를 요청하지 마시오. 특히 6개월 이상의 기간에는 주봉(`interval='1wk'`)을 적극 활용하시오.

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
