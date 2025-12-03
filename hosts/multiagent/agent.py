from host_agent import HostAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
import os

# 4개 분석 에이전트 포트
root_agent = HostAgent([
    'http://localhost:10101',  # technical_analyst
    'http://localhost:10102',  # fundamental_analyst
    'http://localhost:10103',  # sentiment_analyst
    'http://localhost:10104',  # risk_assessor
]).create_agent()

# A2A app for uvicorn
a2a_app = to_a2a(root_agent, port=int(os.getenv('PORT', '12000')))
