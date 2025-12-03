# 🔧 Refactoring Plan: 계층형 아키텍처 전환

**작성일**: 2025-12-03
**상태**: 계획 수립 완료, 구현 대기

---

## 🎯 목표

현재 아키텍처의 문제점을 해결하고 업계 표준에 맞는 계층형 멀티 에이전트 시스템으로 전환

---

## ❌ 현재 문제점

### 1. **포트 충돌**
- `stock_analyst`와 `technical_analyst`가 모두 포트 10101 사용
- 동시 실행 불가능

**위치**:
- `agents/stock_analyst/agent.py:139` → `port=10101`
- `agents/technical_analyst/agent.py:145` → `port=10101`

### 2. **아키텍처 레이어 불일치**
현재 각 분석 에이전트가 직접 MCP에 연결:
```python
# 문제: 분석 에이전트가 데이터 수집도 함
tools=[
    McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command='uvx',
                args=['yfmcp@latest'],
            ),
        ),
    )
]
```

**문제점**:
- ❌ 책임 혼재 (데이터 수집 + 분석)
- ❌ 중복 요청 (4개 에이전트가 각각 요청)
- ❌ 캐싱 불가능
- ❌ Layer 분리 실패

### 3. **Stock Analyst 역할 불명확**
- 설계 문서에 없는 에이전트
- 4개 전문가의 역할을 혼자서 수행 가능
- 존재 이유 불분명

### 4. **데이터 반환 형식**
- 현재: 텍스트만 반환
- 필요: 텍스트 + 구조화된 데이터 (Artifacts)
- UI가 차트/그래프 생성 불가능

---

## ✅ 목표 아키텍처: 3-Layer System

### **업계 표준 패턴**

```
┌─────────────────────────────────────────────────┐
│  User Interface (Mesop UI)                      │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────┐
│  Layer 3: Orchestrator (Host Agent)             │
│  - 전체 워크플로우 관리                          │
│  - 데이터 수집 조율                              │
│  - 분석 결과 통합                                │
│  - 최종 리포트 생성                              │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ↓            ↓            ↓
┌──────────────────────────────────────────────┐
│  Layer 2: Analysis Agents (병렬 실행)        │
│  ┌──────────────┐  ┌──────────────┐         │
│  │  Technical   │  │ Fundamental  │         │
│  │  Analyst     │  │ Analyst      │         │
│  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐         │
│  │  Sentiment   │  │     Risk     │         │
│  │  Analyst     │  │   Assessor   │         │
│  └──────────────┘  └──────────────┘         │
│                                              │
│  - MCP 연결 제거                              │
│  - 데이터를 입력으로 받음                      │
│  - 분석 결과 + Artifacts 반환                 │
└──────────────────────────────────────────────┘
                     ↑
                     │ (데이터 제공)
┌────────────────────┴────────────────────────────┐
│  Layer 1: Data Collection (Host Agent 담당)     │
│  - MCP 서버 연결 (yfmcp)                        │
│  - 데이터 수집 및 정규화                         │
│  - 캐싱 관리                                    │
└─────────────────────────────────────────────────┘
```

---

## 📋 구현 계획

### **Phase 1: 즉시 수정 사항** (1-2일)

#### 1.1 포트 충돌 해결
```bash
# Option A: Stock Analyst 제거 (권장)
rm -rf agents/stock_analyst/

# Option B: Stock Analyst 포트 변경
# agents/stock_analyst/agent.py:139
# port=10101 → port=10105
```

**결정**: Option A (제거) 추천
- 설계 문서에 없는 에이전트
- 역할이 Host Agent와 중복

#### 1.2 에이전트 포트 정리
```
Technical Analyst:   10101 ✅
Fundamental Analyst: 10102 ✅
Sentiment Analyst:   10103 ✅
Risk Assessor:       10104 ✅
```

---

### **Phase 2: Artifacts 구현** (2-3일)

#### 2.1 분석 에이전트 instruction 수정

각 에이전트의 응답 형식을 JSON + Artifacts로 변경:

```python
# agents/technical_analyst/agent.py

instruction = '''
...

**CRITICAL: Response Format with Artifacts**

Return your response in this exact JSON format:

{
  "analysis_text": "[Your full markdown analysis]",
  "artifacts": {
    "price_data": {
      "description": "Historical OHLCV price data",
      "data": [
        {"date": "2025-01-01", "open": 150.0, "high": 155.0, ...}
      ]
    },
    "indicators": {
      "description": "Calculated technical indicators",
      "data": {
        "rsi": 65.5,
        "macd": {...},
        "moving_averages": {...}
      }
    },
    "chart_annotations": {
      "description": "Support and resistance levels",
      "data": [
        {"type": "support", "level": 145.0, "strength": "strong"}
      ]
    }
  },
  "metadata": {
    "ticker": "AAPL",
    "agent": "technical_analyst",
    "timestamp": "2025-12-03T10:00:00Z"
  }
}
'''
```

#### 2.2 Host Agent 파싱 로직 추가

```python
# hosts/multiagent/host_agent.py

async def parse_agent_response(response_text: str) -> dict:
    """에이전트 응답을 파싱하여 텍스트와 Artifacts 분리"""
    try:
        # JSON 파싱 시도
        # ```json ... ``` 코드 블록 제거
        content = response_text.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        parsed = json.loads(content.strip())

        return {
            'text': parsed.get('analysis_text', response_text),
            'artifacts': parsed.get('artifacts', {}),
            'metadata': parsed.get('metadata', {})
        }
    except json.JSONDecodeError:
        # 폴백: 순수 텍스트
        return {
            'text': response_text,
            'artifacts': {},
            'metadata': {}
        }
```

#### 2.3 테스트

```bash
# Artifacts 테스트 스크립트 실행
cd my-a2a-project
uv run python test_artifacts.py
```

**검증 항목**:
- [ ] JSON 파싱 성공
- [ ] analysis_text 존재
- [ ] artifacts.price_data 존재
- [ ] artifacts.indicators 존재
- [ ] artifacts.chart_annotations 존재

---

### **Phase 3: Layer 분리** (3-5일)

#### 3.1 Host Agent에 MCP 추가

```python
# hosts/multiagent/host_agent.py

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Host Agent 생성 시 MCP 도구 추가
root_agent = Agent(
    model=...,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='uvx',
                    args=['yfmcp@latest'],
                ),
            ),
        )
    ],
    ...
)
```

#### 3.2 분석 에이전트에서 MCP 제거

```python
# agents/technical_analyst/agent.py
# agents/fundamental_analyst/agent.py
# agents/sentiment_analyst/agent.py
# agents/risk_assessor/agent.py

# BEFORE:
root_agent = Agent(
    tools=[McpToolset(...)],  # ❌ 제거
    ...
)

# AFTER:
root_agent = Agent(
    # tools 제거 - 데이터는 Host Agent가 제공
    ...
)
```

#### 3.3 Workflow 수정

```python
# hosts/multiagent/host_agent.py

async def analyze_stock(ticker: str):
    # 1. 데이터 수집 (Host Agent가 MCP 사용)
    print(f"📊 Collecting data for {ticker}...")

    market_data = await mcp_tools.get_stock_data(ticker)
    historical_data = await mcp_tools.get_historical_data(
        ticker, period="6mo", interval="1d"
    )
    news_data = await mcp_tools.get_news(ticker)

    # 2. 분석 에이전트에게 데이터와 함께 위임 (병렬)
    print(f"🔬 Delegating analysis to specialists...")

    analyses = await asyncio.gather(
        technical_agent.analyze(
            f"Analyze {ticker} with this data: {historical_data}"
        ),
        fundamental_agent.analyze(
            f"Analyze {ticker} with this data: {market_data}"
        ),
        sentiment_agent.analyze(
            f"Analyze {ticker} with this data: {news_data}"
        ),
        risk_agent.analyze(
            f"Analyze {ticker} with this data: {historical_data}"
        )
    )

    # 3. 결과 파싱
    parsed_results = {}
    for agent_name, response in zip(
        ['technical', 'fundamental', 'sentiment', 'risk'],
        analyses
    ):
        parsed_results[agent_name] = parse_agent_response(response)

    # 4. 최종 종합
    final_report = synthesize_report(parsed_results)

    return final_report
```

---

### **Phase 4: UI 업데이트** (1-2일)

#### 4.1 Mesop UI에서 Artifacts 활용

```python
# demo/ui/pages/analysis_page.py

def display_analysis(analysis_results):
    # 텍스트 분석
    me.markdown(analysis_results['text'])

    # Artifacts 데이터 활용
    if 'artifacts' in analysis_results:
        artifacts = analysis_results['artifacts']

        # 가격 데이터 테이블
        if 'price_data' in artifacts:
            me.text("📊 Price Data", type="headline-6")
            me.data_table(artifacts['price_data']['data'])

        # 지표 카드
        if 'indicators' in artifacts:
            indicators = artifacts['indicators']['data']
            with me.box(style=me.Style(display="flex", gap=10)):
                me.card(f"RSI: {indicators.get('rsi', 'N/A')}")
                me.card(f"MACD: {indicators.get('macd', {}).get('macd_line', 'N/A')}")

        # (나중에) 차트 추가
        # fig = create_candlestick_chart(artifacts['price_data']['data'])
        # me.plotly_chart(fig)
```

---

## 🔍 검증 방법

### 테스트 체크리스트

#### Phase 1: 포트 충돌
```bash
# 모든 에이전트 동시 실행
./run_all.sh

# 포트 확인
lsof -i:10101  # Technical Analyst만
lsof -i:10102  # Fundamental Analyst만
lsof -i:10103  # Sentiment Analyst만
lsof -i:10104  # Risk Assessor만
```

#### Phase 2: Artifacts
```bash
# Artifacts 테스트
uv run python test_artifacts.py

# 기대 결과:
# ✅ JSON Parsing SUCCESS
# ✅ Artifacts Found
# ✅ price_data, indicators, chart_annotations 존재
```

#### Phase 3: Layer 분리
```bash
# Host Agent 테스트
# 기대 동작:
# 1. Host Agent가 MCP로 데이터 수집
# 2. 4개 에이전트에게 데이터 전달
# 3. 각 에이전트가 분석 수행 (MCP 호출 없음)
# 4. Host Agent가 결과 통합
```

#### Phase 4: UI
```bash
# UI 실행 후 수동 테스트
cd demo/ui && uv run main.py

# 브라우저에서 확인:
# - 텍스트 분석 표시 ✅
# - 데이터 테이블 표시 ✅
# - 지표 카드 표시 ✅
```

---

## 📊 예상 일정

| Phase | 작업 | 예상 시간 | 우선순위 |
|-------|------|----------|---------|
| Phase 1 | 포트 충돌 해결 | 0.5일 | P0 (즉시) |
| Phase 2 | Artifacts 구현 | 2-3일 | P1 (중요) |
| Phase 3 | Layer 분리 | 3-5일 | P1 (중요) |
| Phase 4 | UI 업데이트 | 1-2일 | P2 (개선) |

**총 예상**: 1-2주

---

## 💡 중요 참고 자료

### 업계 표준
1. [Orchestrator-Worker Pattern (Azure)](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
2. [Hierarchical Task Decomposition (Google Cloud)](https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system)
3. [Anthropic Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)

### A2A Artifacts
4. [A2A Protocol Core Concepts](https://a2a-protocol.org/latest/topics/key-concepts/)
5. [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/)

### Structured Output
6. [JSON Schema for LLMs](https://superjson.ai/blog/2025-08-17-json-schema-structured-output-apis-complete-guide/)
7. [Structured Output Best Practices](https://dev.to/rishabdugar/crafting-structured-json-responses-ensuring-consistent-output-from-any-llm-l9h)

---

## 🚨 주의사항

### 1. LLM JSON 생성 신뢰성
- Gemini가 항상 정확한 JSON을 반환하지 않을 수 있음
- 파싱 실패 시 폴백 전략 필수
- 마크다운 코드 블록 (```json ... ```) 제거 로직 필요

### 2. 데이터 크기
- 6개월 OHLCV 데이터 = ~130행
- JSON으로 전송 시 크기 고려
- 필요 시 샘플링 또는 요약

### 3. 에이전트 응답 시간
- MCP 호출 + LLM 생성 = 10-30초
- 4개 에이전트 병렬 실행 필요
- 타임아웃 설정 충분히 (120초 이상)

---

## 📝 다음 세션 시작 시

### 바로 시작할 수 있도록:

1. **Phase 1부터 시작**:
   ```bash
   # Stock Analyst 제거
   rm -rf agents/stock_analyst/

   # 포트 확인
   lsof -i:10101
   ```

2. **테스트 스크립트 준비됨**:
   ```bash
   # Artifacts 테스트
   uv run python test_artifacts.py
   ```

3. **문서 참조**:
   - `docs/study_archive/01_MULTI_AGENT_ARCHITECTURE_PATTERNS.md`
   - `docs/study_archive/02_CURRENT_ARCHITECTURE_ANALYSIS.md`
   - `docs/REFACTORING_PLAN.md` (이 파일)

---

**마지막 업데이트**: 2025-12-03
**다음 작업**: Phase 1 - 포트 충돌 해결
**예상 완료**: 2주 이내
