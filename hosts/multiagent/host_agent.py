import asyncio
import base64
import json
import os
import re
import uuid

import httpx

from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from mock_responses import get_mock_manager, is_mock_mode
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
from google.adk.models import Gemini
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
        # Use separate API key for host agent
        host_api_key = os.getenv('GOOGLE_API_KEY_HOST', os.getenv('GOOGLE_API_KEY'))
        return Agent(
            model=Gemini(model='gemini-2.5-flash-lite', api_key=host_api_key),
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
                self.send_messages_parallel,
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

**Stock Analysis Workflow (PARALLEL EXECUTION - FAST):**

When user asks to analyze a stock (e.g., "Analyze Apple stock", "삼성전자 주가 분석해줘", "코어위브 분석해줘"):

1. **Determine the stock ticker:**

   **OPTION A - User provides a ticker symbol directly:**
   - If user provides a clear ticker (AAPL, TSLA, 005930.KS, etc.), use it directly

   **OPTION B - User provides a company name (PREFERRED APPROACH):**
   - **ALWAYS try to identify the most likely ticker from the company name first**
   - Use your knowledge to map common company names to tickers:
     - Apple, 애플 → AAPL
     - Microsoft, 마이크로소프트 → MSFT
     - Tesla, 테슬라 → TSLA
     - Google, Alphabet, 구글 → GOOGL
     - 삼성전자 → 005930.KS
     - SK하이닉스 → 000660.KS
     - NAVER, 네이버 → 035420.KS
     - 카카오 → 035720.KS
     - 현대차 → 005380.KS
     - CoreWeave, 코어위브 → CRWV
     - Nvidia, 엔비디아 → NVDA
     - AMD → AMD

   **IMPORTANT TICKER FORMAT RULES:**
   - **Korean stocks (KOSPI/KOSDAQ)**: ALWAYS add `.KS` suffix (e.g., 005930.KS)
   - **US stocks (NYSE/NASDAQ)**: Use ticker without suffix (e.g., AAPL, CRWV)
   - **If unsure about the exact ticker**: Make your best educated guess based on the company name
   - **For Korean company names in English**: Search for the Korean ticker equivalent

2. **USE PARALLEL ANALYSIS** with `send_messages_parallel(ticker)`:
   - **ALWAYS use `send_messages_parallel(ticker="TICKER")` for stock analysis**
   - This tool queries all 4 analysts (technical, fundamental, sentiment, risk) simultaneously
   - Much faster than calling each analyst individually (~13s vs ~40s)
   - Example: `send_messages_parallel(ticker="AAPL")` or `send_messages_parallel(ticker="005930.KS")`

3. **Synthesize findings in Korean (한국어)** - Combine insights into a comprehensive investment recommendation

**IMPORTANT: Do NOT use send_message 4 times sequentially. ALWAYS use send_messages_parallel for complete stock analysis.**

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
- **For stock analysis: Use `send_messages_parallel(ticker)` to query all 4 analysts at once (RECOMMENDED - 3x faster)**
- For individual queries: Use `send_message(agent_name, message)` to delegate tasks to a single agent

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

    async def send_messages_parallel(
        self, ticker: str, tool_context: ToolContext
    ) -> dict:
        """Query all 4 stock analysis agents in parallel for faster analysis.

        This tool sends the same analysis request to all 4 specialized analysts
        (technical, fundamental, sentiment, risk) simultaneously using asyncio.gather(),
        reducing total analysis time from ~40 seconds to ~13 seconds.

        MOCK MODE: Set USE_MOCK_RESPONSES=true to use cached responses instead of API calls.
        Responses are automatically saved to mock_data/ directory for later replay.

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL", "005930.KS" for Samsung)
            tool_context: The tool context this method runs in.

        Returns:
            A dictionary containing all 4 analyst reports with agent names as keys.
        """
        agent_names = [
            "technical_analyst",
            "fundamental_analyst",
            "sentiment_analyst",
            "risk_assessor"
        ]

        mock_manager = get_mock_manager()

        # Check if we should use mock responses
        if is_mock_mode():
            print(f"[MOCK MODE] Loading cached responses for {ticker}...")
            cached = mock_manager.load_full_analysis(ticker)

            if cached:
                # Return cached responses
                result_text = f"## Parallel Analysis Results for {ticker} [CACHED]\n\n"
                for agent_name in agent_names:
                    result_text += f"### {agent_name.replace('_', ' ').title()}\n"
                    result_text += cached.get(agent_name, "No cached data") + "\n\n"
                print(f"[MOCK MODE] Successfully loaded cached responses for {ticker}")
                return result_text
            else:
                print(f"[MOCK MODE] No cached data for {ticker}, falling back to real API...")

        # Verify all agents are available
        missing_agents = [name for name in agent_names if name not in self.remote_agent_connections]
        if missing_agents:
            raise ValueError(f"Missing agents: {missing_agents}. Available: {list(self.remote_agent_connections.keys())}")

        state = tool_context.state
        context_id = state.get('context_id', None)
        message = f"Analyze {ticker} stock"

        async def query_agent(agent_name: str) -> tuple[str, list]:
            """Query a single agent and return (agent_name, response) with retry logic."""
            max_retries = 3
            base_delay = 2  # Start with 2 seconds

            for attempt in range(max_retries):
                try:
                    client = self.remote_agent_connections[agent_name]
                    request_message = Message(
                        role=Role.user,
                        parts=[Part(root=TextPart(text=message))],
                        message_id=str(uuid.uuid4()),
                        context_id=context_id,
                        task_id=None,
                    )

                    print(f"[Parallel] Querying {agent_name}... (attempt {attempt + 1}/{max_retries})")
                    response = await client.send_message(request_message)
                    print(f"[Parallel] {agent_name} completed")

                    # Process response
                    if isinstance(response, Message):
                        parts = await convert_parts(response.parts, tool_context)
                        return (agent_name, parts)
                    elif isinstance(response, Task):
                        parts = []
                        if response.status.message:
                            parts = await convert_parts(response.status.message.parts, tool_context)
                        if response.artifacts:
                            for artifact in response.artifacts:
                                parts.extend(await convert_parts(artifact.parts, tool_context))
                        return (agent_name, parts)
                    else:
                        return (agent_name, [str(response)])

                except Exception as e:
                    error_str = str(e)
                    is_retryable = ("429" in error_str or
                                  "ResourceExhausted" in error_str or
                                  "RESOURCE_EXHAUSTED" in error_str or
                                  "Timed out" in error_str or
                                  "timeout" in error_str.lower())

                    if is_retryable and attempt < max_retries - 1:
                        # Exponential backoff: 2^attempt * base_delay (2s, 4s, 8s)
                        delay = (2 ** attempt) * base_delay
                        print(f"[Parallel] {agent_name} failed (attempt {attempt + 1}): {error_str}")
                        print(f"[Parallel] Retrying {agent_name} in {delay} seconds...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        # Last attempt or non-retryable error
                        print(f"[Parallel] {agent_name} failed permanently: {e}")
                        error_msg = f"Error from {agent_name}: {error_str}"
                        if "429" in error_str or "ResourceExhausted" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                            error_msg = f"API Quota Exhausted for {agent_name} (after {max_retries} attempts)"
                        elif "Timed out" in error_str or "timeout" in error_str.lower():
                            error_msg = f"Timeout from {agent_name} (after {max_retries} attempts)"

                        mock_json = {
                            "ticker": ticker,
                            "error": True,
                            "analysis_content": f"**[ERROR]** {error_msg}"
                        }
                        return (agent_name, [json.dumps(mock_json, ensure_ascii=False)])

        # Execute all 4 queries in parallel
        print(f"[Parallel] Starting parallel analysis for {ticker}...")
        tasks = [query_agent(name) for name in agent_names]
        results = await asyncio.gather(*tasks)
        print(f"[Parallel] All agents completed for {ticker}")

        # Aggregate results into a structured dictionary
        aggregated = {}
        for agent_name, response_parts in results:
            # Join all parts into a single string for each agent
            if response_parts:
                aggregated[agent_name] = "\n".join(str(part) for part in response_parts)
            else:
                aggregated[agent_name] = f"No response from {agent_name}"

        # Save responses to mock data for future use (always save in real mode)
        if not is_mock_mode():
            print(f"[Parallel] Saving responses to mock_data/ for {ticker}...")
            mock_manager.save_full_analysis(ticker, aggregated)
            # Also save individual responses
            for agent_name in agent_names:
                mock_manager.save_response(ticker, agent_name, aggregated.get(agent_name, ""))

        # Return as a formatted string that the LLM can easily parse
        result_text = f"## Parallel Analysis Results for {ticker}\n\n"
        for agent_name in agent_names:
            result_text += f"### {agent_name.replace('_', ' ').title()}\n"
            result_text += aggregated.get(agent_name, "No data") + "\n\n"

        return result_text


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
