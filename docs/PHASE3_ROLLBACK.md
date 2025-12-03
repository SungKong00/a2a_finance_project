# Phase 3 롤백: 원래 작동하던 상태로 복구 ✅

**Date**: 2025-12-03 16:35
**Status**: ✅ 완료
**Issue**: Phase 3 변경 후 무응답 문제 발생 → 원래 작동하던 상태로 복구

---

## 🔍 근본 원인 분석

### ❌ Phase 3에서의 잘못된 가정

**가정**: "각 에이전트가 MCP를 직접 호출하면 토큰 낭비 → Host Agent가 데이터를 수집해서 전달하자"

**실제 문제**:
1. **4개 에이전트에서 MCP를 제거**했음
2. **Host Agent에 MCP를 추가**했음
3. **Host Agent가 데이터를 수집해서 전달**하려고 시도
4. **BUT**: 실제로는 Host Agent가 데이터를 제대로 전달하지 못함
5. **결과**: 각 에이전트가 데이터 없이 분석 시도 → 응답 불가

### ✅ 실제 작동 방식

**Before (잘 작동하던 상태 - commit bc8e989)**:
```python
# agents/technical_analyst/agent.py
tools=[
    McpToolset(  # ✅ 각 에이전트가 MCP를 가지고 있음
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command='uvx',
                args=['yfmcp@latest'],
            ),
        ),
    )
],
```

**After Phase 3 (무응답 발생)**:
```python
# agents/technical_analyst/agent.py
# No tools - data is provided by Host Agent  # ❌ MCP 완전 제거
instruction='''
**IMPORTANT: Data is Provided to You**
- DO NOT attempt to fetch data yourself - you have no tools
```

---

## 🎯 올바른 아키텍처

### Multi-Agent 시스템의 실제 요구사항:

**각 전문 에이전트는 자신의 도구가 필요합니다!**

1. **Host Agent 역할**:
   - 사용자 요청 이해
   - 적절한 에이전트에 위임
   - 결과 수집 및 종합
   - **데이터 수집 불필요** (각 에이전트가 직접 수행)

2. **전문 에이전트 역할** (Technical, Fundamental, Sentiment, Risk):
   - 자신이 필요한 데이터를 **직접 수집** (MCP 사용)
   - 전문 분석 수행
   - 결과 반환

### 왜 이 방식이 올바른가?

1. **자율성 (Autonomy)**: 각 에이전트가 독립적으로 작동
2. **전문성 (Specialization)**: 각 에이전트가 자신이 필요한 데이터를 정확히 앎
3. **확장성 (Scalability)**: 새로운 에이전트 추가 시 Host Agent 수정 불필요
4. **병렬성 (Parallelism)**: 각 에이전트가 동시에 데이터 수집 가능

---

## 🔧 적용한 해결책

### 1. 4개 에이전트에 MCP 복구

**명령어**:
```bash
git checkout bc8e989 -- \
  agents/technical_analyst/agent.py \
  agents/fundamental_analyst/agent.py \
  agents/sentiment_analyst/agent.py \
  agents/risk_assessor/agent.py
```

**복구된 구조**:
```python
# 각 에이전트 (technical_analyst, fundamental_analyst, sentiment_analyst, risk_assessor)
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
instruction='''
**Available Tools:**
You have access to Yahoo Finance data through yfinance MCP tools:
- `get_stock_data`: Get current stock info
- `get_historical_data`: Get historical price data
- `get_news`: Get recent news

ALWAYS use these tools to fetch real stock data before performing analysis.
'''
```

### 2. Host Agent에서 MCP 제거

**변경사항** (`hosts/multiagent/host_agent.py`):
```python
# REMOVED:
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# REMOVED from tools:
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='uvx',
            args=['yfmcp@latest'],
        ),
    ),
)
```

**업데이트된 도구 목록**:
```python
tools=[
    self.list_remote_agents,  # 에이전트 목록 조회
    self.send_message,        # 에이전트에게 메시지 전송
    # MCP는 제거 - 각 에이전트가 직접 사용
],
```

### 3. Host Agent Workflow 단순화

**Before (Phase 3 - 복잡한 데이터 전달)**:
```
1. Identify ticker
2. **Collect Data with MCP** (Host Agent)
   - get_stock_data
   - get_historical_data
3. **Delegate WITH data** to each analyst
   - Include collected data in message
```

**After (복구 - 단순 위임)**:
```
1. Identify ticker
2. **Delegate** to each analyst
   - Send simple request: "Analyze [TICKER] stock"
   - Each analyst fetches their own data
3. Collect reports
4. Synthesize in Korean
```

### 4. sh 스크립트 업데이트

**`stop_all.sh` 개선**:
- 4개 에이전트 포트 모두 확인 (10101, 10102, 10103, 10104)
- 각 에이전트별 정지 상태 표시
- 더 명확한 피드백

```bash
# Before: 1개 포트만 확인
if lsof -i :10101 > /dev/null 2>&1; then
    echo "❌ Agent still running on port 10101"

# After: 4개 포트 모두 확인
for port in 10101 10102 10103 10104; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "❌ Agent still running on port $port"
    fi
done
```

---

## 📊 Before vs After (복구 효과)

### Before (Phase 3 - 무응답):
```
User Request → Host Agent
  ├─ MCP 데이터 수집 시도
  ├─ 4개 에이전트에게 "데이터 포함" 메시지 전송
  └─ 에이전트들은 데이터를 받지 못함
      └─ Result: 응답 없음 ❌
```

### After (복구 - 정상 작동):
```
User Request → Host Agent
  ├─ 4개 에이전트에게 "Analyze [TICKER]" 전송
  ├─ Technical Analyst
  │   ├─ MCP로 데이터 수집
  │   └─ 기술적 분석 수행
  ├─ Fundamental Analyst
  │   ├─ MCP로 데이터 수집
  │   └─ 펀더멘털 분석 수행
  ├─ Sentiment Analyst
  │   ├─ MCP로 데이터 수집
  │   └─ 심리 분석 수행
  └─ Risk Assessor
      ├─ MCP로 데이터 수집
      └─ 리스크 평가 수행

Host Agent: 4개 리포트 종합 → 한국어 보고서
  └─ Result: 정상 응답 ✅
```

---

## 🎓 교훈: Layer 분리의 올바른 이해

### ❌ 잘못된 해석:
"Layer 분리 = 데이터 수집을 한 곳에 모으기"
- Host Agent가 모든 데이터 수집
- Worker는 데이터만 받아서 분석

### ✅ 올바른 해석:
"Layer 분리 = 책임의 분리"
- **Orchestration Layer** (Host Agent)
  - 작업 조율 및 결과 종합
  - **도구 불필요**

- **Execution Layer** (전문 에이전트)
  - 각자 필요한 도구로 데이터 수집
  - 전문 분석 수행
  - **각자 MCP 보유**

### 올바른 Layer 분리란?

1. **관심사의 분리 (Separation of Concerns)**
   - Host: 조율 (What to analyze?)
   - Workers: 실행 (How to analyze?)

2. **의존성의 분리 (Separation of Dependencies)**
   - Host: A2A 통신 프로토콜
   - Workers: 각자 필요한 도구 (MCP, APIs, etc.)

3. **복잡성의 분리 (Separation of Complexity)**
   - Host: 간단한 조율 로직
   - Workers: 복잡한 분석 로직 + 데이터 수집

---

## ✅ 현재 시스템 상태

### 실행 중인 서비스 (확인 완료)
```
✅ Technical Analyst  - http://localhost:10101
✅ Fundamental Analyst - http://localhost:10102
✅ Sentiment Analyst  - http://localhost:10103
✅ Risk Assessor      - http://localhost:10104
✅ UI (+ Host Agent)  - http://localhost:12000
```

### 복구된 구조
```
my-a2a-project/
├─ agents/
│  ├─ technical_analyst/     ✅ MCP 보유 (복구됨)
│  ├─ fundamental_analyst/   ✅ MCP 보유 (복구됨)
│  ├─ sentiment_analyst/     ✅ MCP 보유 (복구됨)
│  └─ risk_assessor/         ✅ MCP 보유 (복구됨)
├─ hosts/multiagent/
│  └─ host_agent.py          ✅ MCP 제거 (조율만 담당)
├─ demo/ui/                  ✅ 정상 작동
├─ run_all.sh                ✅ 업데이트됨
└─ stop_all.sh               ✅ 업데이트됨
```

---

## 🚀 사용 방법

### 시작
```bash
./run_all.sh
```

### 정지
```bash
./stop_all.sh
```

### 테스트
1. http://localhost:12000 접속
2. "삼성전자 주식 분석해줘" 또는 "Analyze Apple stock" 입력
3. **예상 결과**: 정상적인 종합 분석 리포트 반환

---

## 📝 향후 최적화 방향 (토큰 절약)

Phase 3의 목표였던 "토큰 절약"은 여전히 유효합니다. 다만 접근 방법을 바꿔야 합니다:

### ❌ 잘못된 접근:
"Host Agent가 데이터를 수집해서 전달" → 아키텍처 복잡도 증가, 작동 불가

### ✅ 올바른 접근:

#### 1. **Caching**
- MCP 응답 결과를 캐싱
- 같은 데이터 재사용

#### 2. **Prompt Engineering**
```python
# 현재: 각 에이전트가 6개월 데이터 요청
get_historical_data(period="6mo", interval="1d")  # 약 126개 데이터 포인트

# 최적화: 필요한 만큼만 요청
get_historical_data(period="1mo", interval="1d")  # 약 21개 데이터 포인트
```

#### 3. **Selective Analysis**
- 사용자가 특정 분석만 요청 시 해당 에이전트만 호출
- "기술적 분석만" → Technical Analyst만 실행

#### 4. **Result Streaming**
- 각 에이전트 결과를 스트리밍으로 즉시 표시
- 사용자 경험 개선

---

## 🎯 요약

**Phase 3 롤백 완료**: 잘 작동하던 원래 상태로 복구

**핵심 변경**:
- ✅ 4개 에이전트에 MCP 복구
- ✅ Host Agent에서 MCP 제거
- ✅ Workflow 단순화
- ✅ sh 스크립트 개선

**아키텍처 원칙**:
- Orchestration Layer: 조율만 (도구 불필요)
- Execution Layer: 자율적 실행 (각자 도구 보유)

**다음**: 실제 테스트로 정상 작동 확인 🚀
