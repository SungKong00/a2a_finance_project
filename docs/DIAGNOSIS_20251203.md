# 작업 중단 원인 진단 보고서
**Date**: 2025-12-03 15:59
**Status**: CRITICAL

---

## 🚨 발견된 문제들

### 1. **포트 충돌 - CRITICAL**

**증상**: 10101 포트에 2개의 프로세스가 동시에 실행 중

```bash
Python  17825  :10101 (technical_analyst)
Python  17825  :10102 (fundamental_analyst)
Python  17830  :10103 (sentiment_analyst)
Python  17835  :10104 (risk_assessor)
```

**문제**:
- `stock_analyst` 에이전트가 제거되었지만, Host Agent가 여전히 10101 포트를 사용하려 시도
- `technical_analyst`도 10101 포트 사용 시도
- 포트 충돌로 인해 Host Agent가 멈춤

### 2. **Host Agent 재시작 실패**

**로그**:
```
INFO:     Shutting down
ERROR:    Cancel 0 running task(s), timeout graceful shutdown exceeded
INFO:     Application shutdown complete.
```

**원인**: Host Agent가 정상적으로 shutdown되지 않고 강제 종료됨

### 3. **Stock Analyst API Key 누락**

**에러**:
```python
ValueError: Missing key inputs argument! To use the Google AI API, provide (`api_key`) arguments.
```

**원인**: `agents/stock_analyst/agent.py`에 GOOGLE_API_KEY가 설정되지 않음

### 4. **Technical Analyst 과도한 LLM 호출**

**로그 분석**:
```
15:28:06 - 1번째 Gemini 호출 (28초)
15:29:00 - 2번째 호출 (26초)
15:29:16 - 3번째 호출 (1.5초)
15:29:49 - 4번째 호출 (1.4초)
15:30:14 - 5번째 호출 (1.7초)
15:30:29 - 6번째 호출 (1.3초)
15:30:54 - 7번째 호출 (1.5초)
15:31:51 - 8번째 호출 (56초!)
```

**문제**:
- Technical Analyst가 여전히 MCP를 직접 호출하고 있음
- Phase 3에서 MCP를 제거했지만, 실제로 적용되지 않음
- 에이전트가 도구를 찾으려 시도하면서 다수의 LLM 호출 발생

---

## 🎯 근본 원인

### **Phase 3 변경사항이 실제 적용되지 않음**

우리가 수정한 파일:
- ✅ `agents/technical_analyst/agent.py` - MCP 제거
- ✅ `agents/fundamental_analyst/agent.py` - MCP 제거
- ✅ `agents/sentiment_analyst/agent.py` - MCP 제거
- ✅ `agents/risk_assessor/agent.py` - MCP 제거
- ✅ `hosts/multiagent/host_agent.py` - MCP 추가

**BUT**: 프로세스들이 재시작되지 않아서 **이전 코드**가 계속 실행 중

---

## 🔥 즉시 해야 할 일

### 1. 모든 프로세스 강제 종료
```bash
pkill -9 -f "uvicorn.*10101"
pkill -9 -f "uvicorn.*10102"
pkill -9 -f "uvicorn.*10103"
pkill -9 -f "uvicorn.*10104"
pkill -9 -f "main.py"
```

### 2. Host Agent 포트 변경 (충돌 방지)
- 현재: 12000 (변경 불필요)
- Technical Analyst: 10101 (OK)
- Fundamental: 10102 (OK)
- Sentiment: 10103 (OK)
- Risk: 10104 (OK)

### 3. Stock Analyst 완전 제거
- ❌ 삭제: `agents/stock_analyst/` 폴더 전체
- Phase 1에서 이미 제거했어야 했음

### 4. 모든 에이전트 재시작 (올바른 순서)
```bash
# 1. Host Agent 먼저
cd hosts/multiagent && uv run uvicorn host_agent:a2a_app --port 12000

# 2. 4개 분석 에이전트
cd agents/technical_analyst && uv run uvicorn agent:a2a_app --port 10101
cd agents/fundamental_analyst && uv run uvicorn agent:a2a_app --port 10102
cd agents/sentiment_analyst && uv run uvicorn agent:a2a_app --port 10103
cd agents/risk_assessor && uv run uvicorn agent:a2a_app --port 10104

# 3. UI 마지막
cd demo/ui && uv run main.py
```

---

## 📊 왜 30초가 지나도 응답이 없었나?

**시나리오 재구성**:

1. User가 UI에서 "AAPL 분석해줘" 요청
2. Host Agent가 technical_analyst에게 위임
3. **Technical Analyst (OLD CODE)**:
   - MCP 도구를 찾으려 시도 (15:28:06 - 28초)
   - 도구가 없어서 다시 시도 (15:29:00 - 26초)
   - 여러 번 재시도 (15:29:16, 15:29:49, ...)
   - 결국 timeout (15:31:51 - 56초)
4. Host Agent가 응답을 받지 못하고 hanging
5. UI에서 "working..." 무한 대기

**총 소요 시간**: ~3분 30초 (사용자는 30초 후 포기)

---

## ✅ 해결 완료 후 검증

### 테스트 시나리오:
1. "AAPL 분석해줘" 요청
2. **예상 흐름**:
   - Host Agent: get_stock_data, get_historical_data (10초)
   - Technical Analyst: 데이터 분석만 (5초)
   - 나머지 3개 에이전트: 병렬 분석 (5초)
   - Host Agent: 종합 (5초)
   - **총 25초 이내 완료**

3. **로그 확인**:
   - Technical Analyst가 MCP 호출 시도 없음
   - LLM 호출 1번만
   - Host Agent가 MCP 호출 2번 (stock_data, historical_data)

---

## 🎓 교훈

1. **코드 변경 후 반드시 재시작**
   - 파일 수정 ≠ 실행 중인 프로세스 변경
   - `--reload` 옵션이 있어도 모든 변경사항이 반영되지 않을 수 있음

2. **포트 충돌 사전 방지**
   - 에이전트 제거 시 포트도 함께 정리
   - 시작 전 `lsof -i :<port>` 확인

3. **로그 모니터링**
   - 이상 징후 조기 발견
   - LLM 호출 횟수 = 비용 = 문제의 지표

4. **Clean State 유지**
   - 작업 전 모든 프로세스 종료
   - 깨끗한 상태에서 시작
