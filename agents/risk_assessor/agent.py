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
    model=Gemini(model='gemini-2.5-flash'),
    description='Expert risk analyst specializing in volatility, beta, VIX, and portfolio risk metrics',
    instruction="""리스크 분석가. 주식의 변동성과 하방 리스크를 분석합니다.

도구: get_ticker_info (베타 조회용만 사용)

JSON만 응답:
```json
{"ticker":"AAPL","risk_level":"보통","beta":1.25,"volatility":0.28,"max_drawdown":-0.15,"sharpe_ratio":1.2,"summary":"분석 요약 2문장"}
```
- risk_level: 낮음/보통/높음/매우 높음
- beta: 0.5-2.0 범위
- volatility: 소수점 (28%=0.28)
- max_drawdown: 음수 (15%=-0.15)
- summary: 한국어 2문장
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
a2a_app = to_a2a(root_agent, port=int(os.getenv('PORT', '10104')))
