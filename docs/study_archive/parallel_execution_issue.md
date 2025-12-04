# 병렬 실행 시도와 ToolContext 상태 충돌 문제

**작성일**: 2025-12-04
**주제**: Google ADK의 ToolContext를 공유한 asyncio.gather() 병렬 실행 문제

---

## 1. 전의 구현 내용

### 1.1 문제 인식
- **성능 문제**: 4개의 전문 분석 에이전트(Technical, Fundamental, Sentiment, Risk)를 순차적으로 호출하여 약 30초의 응답 시간 발생
- **병목 지점**: 각 에이전트가 8초씩 소요되어 총 30초 (8s + 8s + 7s + 7s)

### 1.2 구현한 해결 방법
`hosts/multiagent/host_agent.py`에 `analyze_stock_parallel` 메서드를 추가하여 `asyncio.gather()`를 사용한 병렬 실행 구현:

```python
async def analyze_stock_parallel(
    self, ticker: str, tool_context: ToolContext
):
    """Analyze a stock by querying all 4 specialized analysts in parallel."""
    analyst_names = [
        "technical_analyst",
        "fundamental_analyst",
        "sentiment_analyst",
        "risk_assessor"
    ]

    # Create tasks for parallel execution
    tasks = []
    for analyst in analyst_names:
        task = self.send_message(
            analyst_name=analyst,
            message=f"Analyze {ticker} stock",
            tool_context=tool_context  # ⚠️ 문제: 모든 태스크가 동일한 객체 공유
        )
        tasks.append(task)

    # Execute all analyst queries in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # ... 결과 처리
```

### 1.3 기대한 효과
- 병렬 실행으로 30초 → 8-10초로 단축 (70% 성능 향상)
- Gemini 2.0 Flash의 빠른 TTFT (<700ms)와 병렬 호출 지원 활용

---

## 2. 문제점

### 2.1 발생한 현상
- **Host Agent 크래시**: 병렬 실행 시도 후 무한 working 상태 발생
- **에러 로그**:
  ```
  ERROR:    Cancel 0 running task(s), timeout graceful shutdown exceeded
  INFO:     Shutting down
  ```

### 2.2 근본 원인 분석

#### 2.2.1 ToolContext의 상태 공유 문제
Google ADK의 `ToolContext`는 세션 상태를 관리하는 객체로, 내부적으로 `state` 딕셔너리를 가지고 있습니다:

```python
tool_context.state['agent'] = 'technical_analyst'  # Task 1
tool_context.state['context_id'] = '...'           # Task 1
tool_context.state['agent'] = 'fundamental_analyst' # Task 2 (동시 수정!)
```

**문제**: 4개의 병렬 비동기 태스크가 **동일한 `tool_context` 객체**를 참조하여, 동시에 `state`를 수정하려고 시도

#### 2.2.2 State Delta 이벤트 충돌
[Google ADK 공식 문서](https://google.github.io/adk-docs/context/)에 따르면:

> "When your code modifies the session state, this change is initially recorded locally within the current InvocationContext. The change is only guaranteed to be persisted after the Event carrying the corresponding state_delta in its actions has been yielded by your code."

- ADK는 상태 변경을 `state_delta` 이벤트로 추적
- 여러 task가 동시에 상태를 수정하면 이벤트 순서가 꼬임
- 결과적으로 내부 상태 불일치로 인해 타임아웃 및 크래시 발생

#### 2.2.3 ADK의 실행 모델 가정
- ADK의 tool execution model은 **순차 실행을 가정**
- `ToolContext`는 thread-safe하지 않음
- 병렬 실행을 위해서는 각 task가 독립적인 상태 관리 메커니즘 필요

### 2.3 교차 검증 결과
웹 검색을 통해 확인한 공식 권장사항:

1. **[Google ADK - Parallel Agents](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/)**:
   > "Each sub-agent operates in its own execution branch. However, they share the same session state. Ensure state keys don't conflict by using isolated state keys for each agent."

2. **[Azure Architecture - AI Agent Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)**:
   > "Avoid parallel when agents can't reliably coordinate changes to shared state or external systems while running simultaneously."

---

## 3. 해결 원리 및 해결 방안

### 3.1 해결 원리

병렬 실행을 안전하게 수행하려면 **상태 격리(State Isolation)**가 필요합니다:

```
[잘못된 접근]
Task1 ─┐
Task2 ─┼─> 동일한 tool_context.state 공유 ❌
Task3 ─┤
Task4 ─┘

[올바른 접근]
Task1 ─> state['task1']  ✅
Task2 ─> state['task2']  ✅
Task3 ─> state['task3']  ✅
Task4 ─> state['task4']  ✅
```

### 3.2 해결 방안 비교

| 방안 | 안정성 | 성능 | 구현 난이도 | 권장도 |
|-----|-------|------|-----------|--------|
| **방안 1: 순차 실행 유지** | ⭐⭐⭐⭐⭐ | ⭐⭐ (30s) | ⭐⭐⭐⭐⭐ 쉬움 | ✅ 즉시 채택 |
| **방안 2: ParallelAgent 패턴** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (8-10s) | ⭐⭐⭐ 중간 | ⭐⭐⭐⭐⭐ 최선 (향후) |
| **방안 3: LLM 빠른 순차 호출** | ⭐⭐⭐⭐ | ⭐⭐⭐ (15-20s) | ⭐⭐⭐⭐ 쉬움 | ⭐⭐ 차선 |
| 방안 4: asyncio.gather (현재) | ⭐ 크래시 | - | - | ❌ 사용 금지 |

### 3.3 채택한 해결 방안: 순차 실행 복원

#### 즉시 적용 (방안 1)
1. `analyze_stock_parallel` 메서드 제거
2. Host Agent instruction을 순차 실행 방식으로 복구
3. Tools 리스트에서 병렬 도구 제거

**코드 변경사항**:

```python
# hosts/multiagent/host_agent.py

# BEFORE (병렬 실행)
tools=[
    self.list_remote_agents,
    self.send_message,
    self.analyze_stock_parallel,  # 제거
],

instruction="""
2. **Use the `analyze_stock_parallel` tool** - This executes all 4 analyst queries simultaneously
"""

# AFTER (순차 실행)
tools=[
    self.list_remote_agents,
    self.send_message,
    # analyze_stock_parallel 제거됨
],

instruction="""
2. **Query each specialized analyst** using the `send_message` tool:
   - `send_message(analyst_name="technical_analyst", message="Analyze [TICKER] stock")`
   - `send_message(analyst_name="fundamental_analyst", message="Analyze [TICKER] stock")`
   - `send_message(analyst_name="sentiment_analyst", message="Analyze [TICKER] stock")`
   - `send_message(analyst_name="risk_assessor", message="Analyze [TICKER] stock")`
"""
```

#### 향후 개선 방향 (방안 2)

[Google ADK 공식 권장 패턴](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/)인 **ParallelAgent**를 사용:

```python
from google.adk.agents import ParallelAgent

# 각 analyst를 독립적인 Agent 객체로 구성
parallel_analyst = ParallelAgent(
    agents=[
        technical_analyst_agent,
        fundamental_analyst_agent,
        sentiment_analyst_agent,
        risk_assessor_agent
    ],
    output_key_mapping={
        "technical_analyst": "technical_analysis",
        "fundamental_analyst": "fundamental_analysis",
        "sentiment_analyst": "sentiment_analysis",
        "risk_assessor": "risk_analysis"
    }
)
```

**장점**:
- ADK가 내부적으로 상태 격리 처리
- 각 agent가 독립적인 `output_key` 사용하여 충돌 방지
- 공식 문서 권장 패턴
- 30초 → 8-10초 성능 향상 가능

**구현 요구사항**:
- 각 analyst를 A2A 서버가 아닌 ADK Agent 객체로 재구성 필요
- Host Agent 아키텍처 리팩토링 필요
- 현재의 분산 A2A 서버 구조와 다른 접근 방식

---

## 4. 효과

### 4.1 방안 1 (순차 실행 복원)의 효과

#### 긍정적 효과
✅ **시스템 안정성 확보**
- Host Agent 크래시 문제 해결
- 무한 working 상태 제거
- 예측 가능한 동작 보장

✅ **코드 단순화**
- 복잡한 병렬 처리 로직 제거
- 디버깅 및 유지보수 용이
- 에러 추적 명확

✅ **즉시 적용 가능**
- 최소한의 코드 변경
- 추가 테스트 불필요
- 기존 동작 방식으로 안전하게 복귀

#### 트레이드오프
⚠️ **응답 시간 증가**
- 30초의 응답 시간 유지 (병렬 8-10초 대비)
- 사용자 경험 측면에서 개선 필요

### 4.2 방안 2 (ParallelAgent 패턴)의 기대 효과

#### 구현 시 예상 효과
🚀 **성능 개선**
- 70% 응답 시간 단축 (30초 → 8-10초)
- [Medium 가이드](https://medium.com/google-cloud/2-minute-adk-speed-up-your-agent-with-parallel-tools-56450c3edb64)에서 검증된 패턴
- 사용자 경험 크게 향상

🛡️ **안정성 유지**
- 공식 권장 방법으로 ADK가 상태 관리
- 프로덕션 환경에 안전하게 배포 가능
- 확장성 있는 아키텍처

📚 **학습 가치**
- Google ADK의 multi-agent orchestration 패턴 이해
- 상태 관리와 병렬 처리의 trade-off 학습
- 분산 시스템 설계의 실전 경험

---

## 5. 학습 포인트 정리

### 5.1 핵심 교훈

1. **상태 공유는 병렬 처리의 적**
   - 여러 비동기 task가 동일한 mutable 객체를 수정하면 race condition 발생
   - 상태 격리(State Isolation) 또는 불변성(Immutability) 필요

2. **프레임워크의 실행 모델 이해 필수**
   - Google ADK의 ToolContext는 순차 실행을 가정
   - 병렬 처리를 원한다면 프레임워크가 제공하는 공식 패턴(ParallelAgent) 사용

3. **성능 최적화는 단계적으로**
   - 먼저 안정성 확보 → 프로파일링 → 병목 지점 파악 → 올바른 방법으로 최적화
   - 잘못된 병렬 처리는 순차 처리보다 못할 수 있음 (크래시 등)

### 5.2 디버깅 방법론

1. **로그 확인**: Host Agent와 Specialist Agent 로그 동시 확인
2. **프로세스 상태 확인**: `lsof -ti :PORT`로 프로세스 생존 여부 확인
3. **공식 문서 참조**: 프레임워크 공식 문서에서 권장 패턴 확인
4. **웹 검색 교차 검증**: 커뮤니티에서 유사한 문제 해결 사례 조사

### 5.3 관련 참고 자료

- [Google ADK - Parallel Agents](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/)
- [Google ADK - Context Management](https://google.github.io/adk-docs/context/)
- [2-Minute ADK: Speed Up Your Agent with Parallel Tools](https://medium.com/google-cloud/2-minute-adk-speed-up-your-agent-with-parallel-tools-56450c3edb64)
- [Google ADK Masterclass Part 10: Parallel Execution Workflows](https://saptak.in/writing/2025/05/10/google-adk-masterclass-part10)
- [AI Agent Orchestration Patterns - Azure](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [A2A Protocol Official Specification](https://a2a-protocol.org/latest/specification/)

---

## 6. 실습 가이드

### 6.1 문제 재현 방법 (교육 목적)

```bash
# 1. 현재 stable 브랜치 확인
git branch

# 2. 문제가 있는 병렬 실행 코드 확인
cat hosts/multiagent/host_agent.py | grep -A 30 "analyze_stock_parallel"

# 3. Host Agent 실행
cd demo/ui && uv run main.py &

# 4. UI에서 주식 분석 요청 후 무한 working 발생 확인

# 5. 로그 확인
# Host Agent 로그에서 "ERROR: Cancel 0 running task(s)" 메시지 확인
```

### 6.2 해결 방법 적용 실습

```bash
# 1. analyze_stock_parallel 메서드 제거
# hosts/multiagent/host_agent.py의 Line 368-431 삭제

# 2. instruction 수정
# Line 145-151을 순차 실행 방식으로 변경

# 3. tools 리스트 수정
# Line 108에서 self.analyze_stock_parallel 제거

# 4. Host Agent 재시작
lsof -ti :12000 | xargs kill -9
cd demo/ui && uv run main.py &

# 5. 테스트
# UI에서 주식 분석 요청 후 정상 작동 확인 (30초 소요)
```

### 6.3 향후 ParallelAgent 구현 실습 (Advanced)

```bash
# 1. 각 analyst를 A2A 서버에서 ADK Agent로 변환
# 2. ParallelAgent 구성
# 3. Host Agent에 통합
# 4. 성능 측정 및 비교

# 구현 예정 - 현재 문서 작성 시점에는 순차 실행 복원이 우선
```

---

**작성자 노트**: 이 문서는 실제 프로젝트에서 발생한 문제를 분석하고 해결하는 과정을 기록한 학습 자료입니다. 동일한 문제를 겪는 다른 개발자들에게 도움이 되기를 바랍니다.
