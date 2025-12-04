import asyncio
import base64
import json
import os
import re
import uuid

import httpx

from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import (
    AgentCard,
    DataPart,
    Message,
    Part,
    Role,
    Task,
    TaskState,
    TextPart,
    TransportProtocol,
)
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from remote_agent_connection import RemoteAgentConnections, TaskUpdateCallback
from timestamp_ext import TimestampExtension


class HostAgent:
    """The host agent.

    This is the agent responsible for choosing which remote agents to send
    tasks to and coordinate their work.
    """

    def __init__(
        self,
        remote_agent_addresses: list[str],
        http_client: httpx.AsyncClient,
        task_callback: TaskUpdateCallback | None = None,
    ):
        self.task_callback = task_callback
        self.httpx_client = http_client
        self.timestamp_extension = TimestampExtension()
        config = ClientConfig(
            httpx_client=self.httpx_client,
            supported_transports=[
                TransportProtocol.jsonrpc,
                TransportProtocol.http_json,
            ],
        )
        client_factory = ClientFactory(config)
        client_factory = self.timestamp_extension.wrap_client_factory(
            client_factory
        )
        self.client_factory = client_factory
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ''
        loop = asyncio.get_running_loop()
        loop.create_task(
            self.init_remote_agent_addresses(remote_agent_addresses)
        )

    async def init_remote_agent_addresses(
        self, remote_agent_addresses: list[str]
    ):
        async with asyncio.TaskGroup() as task_group:
            for address in remote_agent_addresses:
                task_group.create_task(self.retrieve_card(address))
        # The task groups run in the background and complete.
        # Once completed the self.agents string is set and the remote
        # connections are established.

    async def retrieve_card(self, address: str):
        card_resolver = A2ACardResolver(self.httpx_client, address)
        card = await card_resolver.get_agent_card()
        self.register_agent_card(card)

    def register_agent_card(self, card: AgentCard):
        remote_connection = RemoteAgentConnections(self.client_factory, card)
        self.remote_agent_connections[card.name] = remote_connection
        self.cards[card.name] = card
        agent_info = []
        for ra in self.list_remote_agents():
            agent_info.append(json.dumps(ra))
        self.agents = '\n'.join(agent_info)

    def create_agent(self) -> Agent:
        LITELLM_MODEL = os.getenv(
            'LITELLM_MODEL', 'gemini/gemini-2.0-flash-001'
        )
        return Agent(
            model=LiteLlm(model=LITELLM_MODEL),
            name='host_agent',
            instruction=self.root_instruction,
            before_model_callback=self.before_model_callback,
            description=(
                'This agent orchestrates the decomposition of the user request into'
                ' tasks that can be performed by the child agents.'
            ),
            tools=[
                self.list_remote_agents,
                self.send_message,
            ],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        current_agent = self.check_state(context)
        return f"""You are an expert financial analyst coordinator managing a team of 4 specialized stock analysis agents.

**CRITICAL: ALWAYS respond in Korean (한국어) regardless of the language used in the user's question or analyst responses.**

**Your Role:**
- Coordinate between user requests and specialized analysts
- Delegate stock analysis tasks to appropriate experts
- Synthesize insights from multiple analysts into comprehensive recommendations
- **Present all findings in Korean (한국어)**

**Available Specialized Analysts:**

1. **technical_analyst**: Chart patterns, RSI, MACD, Moving Averages, support/resistance levels, entry/exit points
2. **fundamental_analyst**: P/E ratios, earnings, revenue growth, financial health, ROE, ROA, valuation metrics
3. **sentiment_analyst**: News sentiment, analyst ratings, market mood, social media buzz, upcoming catalysts
4. **risk_assessor**: Volatility, beta, VIX context, maximum drawdown, portfolio fit, position sizing

**Stock Analysis Workflow:**

When user asks to analyze a stock (e.g., "Analyze Apple stock", "삼성전자 주가 분석해줘"):

1. **Identify the stock ticker** from the user's request
   - **IMPORTANT: For Korean stocks, use the correct Yahoo Finance ticker format:**
     - 삼성전자 → 005930.KS (NOT SMSN.IL)
     - SK하이닉스 → 000660.KS
     - NAVER → 035420.KS
     - 카카오 → 035720.KS
     - 현대차 → 005380.KS
   - For US stocks: Use standard tickers (AAPL, TSLA, MSFT, GOOGL, etc.)
   - If unsure, default to .KS suffix for Korean stocks

2. **Query each specialized analyst** using the `send_message` tool:
   - `send_message(analyst_name="technical_analyst", message="Analyze [TICKER] stock")`
   - `send_message(analyst_name="fundamental_analyst", message="Analyze [TICKER] stock")`
   - `send_message(analyst_name="sentiment_analyst", message="Analyze [TICKER] stock")`
   - `send_message(analyst_name="risk_assessor", message="Analyze [TICKER] stock")`
   - Each analyst will independently fetch data and perform their specialized analysis

3. **Collect all 4 reports** - Wait for each analyst to complete their analysis

4. **Synthesize findings in Korean (한국어)** - Combine insights into a comprehensive investment recommendation

**Synthesis Guidelines (한국어로 작성):**
- 경영 요약(Executive Summary)으로 시작
- 각 분석가의 핵심 발견사항을 해당 섹션에 제시
- 합의된 견해와 상충되는 신호 식별
- 4가지 관점을 모두 고려한 최종 권고안 제공
- 주요 위험요소 및 실행 항목 포함

**Korean Output Format Template:**
```
## 종합 분석 보고서: [회사명] ([티커])

### 📊 경영 요약
[전반적인 투자 의견을 2-3문장으로 요약]

### 📈 기술적 분석 (Technical Analyst)
[기술적 분석가의 핵심 발견사항]

### 💼 펀더멘털 분석 (Fundamental Analyst)
[펀더멘털 분석가의 핵심 발견사항]

### 📰 시장 심리 분석 (Sentiment Analyst)
[심리 분석가의 핵심 발견사항]

### ⚠️ 리스크 평가 (Risk Assessor)
[리스크 평가자의 핵심 발견사항]

### 🎯 종합 의견
- **합의 사항**: [분석가들 간 일치하는 견해]
- **상충 사항**: [분석가들 간 다른 견해]
- **최종 권고**: [매수/보유/매도 및 근거]

### ⚠️ 주요 리스크
- [리스크 1]
- [리스크 2]
- [리스크 3]

### ✅ 실행 항목
- [실행 항목 1]
- [실행 항목 2]

---
### 🔍 데이터 검증 (UI Debug)
*이 섹션은 구조화된 데이터 반환을 검증하기 위한 디버그 정보입니다.*

**Technical Analyst Data:**
```json
[Technical Analyst로부터 받은 원본 JSON 데이터를 여기에 그대로 출력]
```

**Fundamental Analyst Data:**
```json
[Fundamental Analyst로부터 받은 원본 JSON 데이터를 여기에 그대로 출력]
```

**Sentiment Analyst Data:**
```json
[Sentiment Analyst로부터 받은 원본 JSON 데이터를 여기에 그대로 출력]
```

**Risk Assessor Data:**
```json
[Risk Assessor로부터 받은 원본 JSON 데이터를 여기에 그대로 출력]
```
```

**Important:**
- **ALWAYS write your final synthesis in Korean (한국어)**
- For stock analysis requests, ALWAYS delegate to all 4 analysts
- For non-stock questions, use appropriate agents or respond directly in Korean
- Be sure to include the analyst names when presenting their findings
- Don't make up responses - rely on actual analyst outputs
- Translate and summarize English analyst responses into Korean
- **JSON Extraction**: Each analyst will return a JSON block at the end of their response. You MUST extract this JSON block and place it in the "Data Verification (UI Debug)" section exactly as received.

**Discovery:**
- Use `list_remote_agents` to see available analysts

**Execution:**
- Use `send_message(agent_name, message)` to delegate tasks

Available Agents:
{self.agents}

Current agent: {current_agent['active_agent']}
"""

    def check_state(self, context: ReadonlyContext):
        state = context.state
        if (
            'context_id' in state
            and 'session_active' in state
            and state['session_active']
            and 'agent' in state
        ):
            return {'active_agent': f'{state["agent"]}'}
        return {'active_agent': 'None'}

    def before_model_callback(
        self, callback_context: CallbackContext, llm_request
    ):
        state = callback_context.state
        if 'session_active' not in state or not state['session_active']:
            state['session_active'] = True

    def list_remote_agents(self):
        """List the available remote agents you can use to delegate the task."""
        if not self.remote_agent_connections:
            return []

        remote_agent_info = []
        for card in self.cards.values():
            remote_agent_info.append(
                {'name': card.name, 'description': card.description}
            )
        return remote_agent_info

    async def send_message(
        self, agent_name: str, message: str, tool_context: ToolContext
    ):
        """Sends a task either streaming (if supported) or non-streaming.

        This will send a message to the remote agent named agent_name.

        Args:
          agent_name: The name of the agent to send the task to.
          message: The message to send to the agent for the task.
          tool_context: The tool context this method runs in.

        Yields:
          A dictionary of JSON data.
        """
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f'Agent {agent_name} not found')
        state = tool_context.state
        state['agent'] = agent_name
        client = self.remote_agent_connections[agent_name]
        if not client:
            raise ValueError(f'Client not available for {agent_name}')
        # Do NOT pass task_id to sub-agents - they should create their own tasks
        # task_id = state.get('task_id', None)
        context_id = state.get('context_id', None)
        message_id = state.get('message_id', None)
        task: Task
        if not message_id:
            message_id = str(uuid.uuid4())

        request_message = Message(
            role=Role.user,
            parts=[Part(root=TextPart(text=message))],
            message_id=message_id,
            context_id=context_id,
            task_id=None,  # Let sub-agent create its own task
        )
        print(f"HostAgent: Sending message to {agent_name}...")
        try:
            response = await client.send_message(request_message)
        except Exception as e:
            print(f"HostAgent: Error communicating with {agent_name}: {e}")
            error_msg = f"Error: Failed to get response from {agent_name}. "
            if "429" in str(e) or "ResourceExhausted" in str(e):
                error_msg += "API Quota Exhausted (429). Please try again later."
            else:
                error_msg += str(e)
            
            # Return a mock JSON response so the UI doesn't hang
            mock_json = {
                "ticker": "ERROR",
                "analysis_content": f"**[SYSTEM ERROR]**\n\n{error_msg}\n\n(This is a system generated message to prevent infinite loading.)"
            }
            return [json.dumps(mock_json)]
        print(f"HostAgent: Received response from {agent_name}")
        if isinstance(response, Message):
            return await convert_parts(response.parts, tool_context)
        task: Task = response
        # Assume completion unless a state returns that isn't complete
        state['session_active'] = task.status.state not in [
            TaskState.completed,
            TaskState.canceled,
            TaskState.failed,
            TaskState.unknown,
        ]
        if task.context_id:
            state['context_id'] = task.context_id
        state['task_id'] = task.id
        if task.status.state == TaskState.input_required:
            # Force user input back
            tool_context.actions.skip_summarization = True
            tool_context.actions.escalate = True
        elif task.status.state == TaskState.canceled:
            # Open question, should we return some info for cancellation instead
            raise ValueError(f'Agent {agent_name} task {task.id} is cancelled')
        elif task.status.state == TaskState.failed:
            # Raise error for failure
            raise ValueError(f'Agent {agent_name} task {task.id} failed')
        response = []
        if task.status.message:
            # Assume the information is in the task message.
            if ts := self.timestamp_extension.get_timestamp(
                task.status.message
            ):
                response.append(f'[at {ts.astimezone().isoformat()}]')
            response.extend(
                await convert_parts(task.status.message.parts, tool_context)
            )
        if task.artifacts:
            for artifact in task.artifacts:
                if ts := self.timestamp_extension.get_timestamp(artifact):
                    response.append(f'[at {ts.astimezone().isoformat()}]')
                response.extend(
                    await convert_parts(artifact.parts, tool_context)
                )
        return response


async def convert_parts(parts: list[Part], tool_context: ToolContext):
    rval = []
    for p in parts:
        rval.append(await convert_part(p, tool_context))
    return rval


async def convert_part(part: Part, tool_context: ToolContext):
    if part.root.kind == 'text':
        text = part.root.text
        # Try to extract JSON block from markdown response
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group(1))
                # Return both the original text and the extracted JSON
                # This allows the Host Agent to use the JSON for synthesis
                # while preserving the full markdown report
                return json.dumps(json_data, ensure_ascii=False)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse JSON from text: {e}")
                # Fall through to return original text
        return text
    if part.root.kind == 'data':
        # Convert data to JSON string for the LLM to consume as text
        return json.dumps(part.root.data, ensure_ascii=False)
    if part.root.kind == 'file':
        # Repackage A2A FilePart to google.genai Blob
        # Currently not considering plain text as files
        file_id = part.root.file.name
        file_bytes = base64.b64decode(part.root.file.bytes)
        file_part = types.Part(
            inline_data=types.Blob(
                mime_type=part.root.file.mime_type, data=file_bytes
            )
        )
        await tool_context.save_artifact(file_id, file_part)
        tool_context.actions.skip_summarization = True
        tool_context.actions.escalate = True
        return DataPart(data={'artifact-file-id': file_id})
    return f'Unknown type: {part.kind}'
