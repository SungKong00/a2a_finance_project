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
    model=Gemini(model='gemini-2.5-flash'),
    description='Expert fundamental analyst specializing in financial statements, valuation metrics, and company analysis',
    instruction="""펀더멘털 분석가. 주식의 재무 건전성과 밸류에이션을 분석합니다.

도구: get_ticker_info

JSON만 응답:
```json
{"ticker":"AAPL","valuation_verdict":"적정가","pe_ratio":28.5,"pb_ratio":45.2,"market_cap":2850000000000,"revenue_growth":0.08,"roe":0.147,"recommendation":"매수","summary":"분석 요약 2문장"}
```
- valuation_verdict: 저평가/적정가/고평가
- recommendation: 적극 매수/매수/보유/매도/적극 매도
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
a2a_app = to_a2a(root_agent, port=int(os.getenv('PORT', '10102')))
