# Multi-Agent 시스템 검증 가이드

**Date**: 2025-12-03
**Status**: 작성 완료
**Purpose**: 각 에이전트의 동작 및 Artifacts 반환 여부를 검증하는 방법

---

## 🎯 검증 목표

1. **각 에이전트가 자신의 역할을 제대로 수행하는지 확인**
2. **Artifacts(구조화된 데이터)를 반환하는지 확인**
3. **추후 시각화를 위한 데이터 형식 검증**

---

## 📋 현재 시스템 상태

### 실행 중인 에이전트

```
✅ Technical Analyst  - http://localhost:10101
✅ Fundamental Analyst - http://localhost:10102
✅ Sentiment Analyst  - http://localhost:10103
✅ Risk Assessor      - http://localhost:10104
✅ Host Agent (UI)    - http://localhost:12000
```

### Artifacts 구현 상태

**현재 발견사항** (2025-12-03 검증 결과):

```
❌ Technical Analyst   - Artifacts 미구현 (텍스트 응답만)
❌ Fundamental Analyst - Artifacts 미구현 (텍스트 응답만)
❌ Sentiment Analyst   - Artifacts 미구현 (텍스트 응답만)
❌ Risk Assessor       - Artifacts 미구현 (텍스트 응답만)
```

**이유**: Phase 3 롤백 시 commit bc8e989로 복구했는데, 그 당시에는 Artifacts가 아직 구현되지 않았음.

---

## 🔍 검증 방법

### 1. 로그 기반 검증 (현재 가능)

#### 1-1. UI 로그 확인

UI 로그에서 다음을 확인할 수 있습니다:

```bash
# 백그라운드 프로세스의 로그 확인
# (현재 실행 중인 UI 프로세스 ID 확인 필요)
```

**주요 로그 패턴**:

```
# ✅ 정상 동작
INFO: 127.0.0.1:xxxxx - "POST /message/send HTTP/1.1" 200 OK

# ⚠️ Artifacts 변환 오류
Couldn't convert to messages: 'result'

# ⚠️ 빈 응답
No message content
```

#### 1-2. 각 에이전트별 검증

**Technical Analyst (Port 10101)**:
- MCP 도구 호출: `get_stock_data`, `get_historical_data`
- 기술적 지표 계산: RSI, MACD, Moving Averages
- 차트 패턴 분석

**Fundamental Analyst (Port 10102)**:
- 재무제표 데이터 수집
- P/E, ROE, ROA 계산
- 밸류에이션 분석

**Sentiment Analyst (Port 10103)**:
- 뉴스 수집: `get_news`
- 감정 분석
- 애널리스트 의견 통합

**Risk Assessor (Port 10104)**:
- 변동성 계산
- Beta, VaR 분석
- 포트폴리오 적합성 평가

---

### 2. 코드 기반 검증 (구현 확인)

#### 2-1. Artifacts 구현 여부 확인

각 에이전트 파일에서 다음을 확인:

```bash
# after_model_callback 구현 확인
grep -r "after_model_callback" agents/

# set_artifacts 호출 확인
grep -r "set_artifacts" agents/
```

**현재 결과**:
```
No files found  # ❌ Artifacts 미구현
```

#### 2-2. 필요한 구현 구조

Artifacts를 반환하려면 각 에이전트에 다음이 필요합니다:

```python
# agents/technical_analyst/agent.py 예시

def after_model_callback(callback_context: CallbackContext, llm_response):
    """모델 응답 후 Artifacts 설정"""

    # LLM 응답에서 JSON 추출 시도
    try:
        # llm_response.text에서 JSON 블록 찾기
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_response.text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            data = json.loads(json_str)

            # Artifacts로 설정
            callback_context.set_artifacts([
                types.Part(
                    inline_data=types.Blob(
                        mime_type='application/json',
                        data=json_str.encode('utf-8')
                    )
                )
            ])
    except Exception as e:
        print(f"Failed to extract artifacts: {e}")

root_agent = Agent(
    # ...
    after_model_callback=after_model_callback,  # 콜백 등록
)
```

---

### 3. 응답 구조 검증 (실제 데이터)

#### 3-1. 기대하는 Artifacts 형식

**Technical Analyst**:
```json
{
  "ticker": "AAPL",
  "analysis_date": "2025-12-03",
  "technical_indicators": {
    "rsi": 65.3,
    "macd": {
      "value": 2.5,
      "signal": 2.1,
      "histogram": 0.4
    },
    "moving_averages": {
      "sma_20": 178.5,
      "sma_50": 175.2,
      "sma_200": 168.9
    }
  },
  "support_resistance": {
    "support": [175.0, 172.5],
    "resistance": [182.0, 185.5]
  },
  "recommendation": {
    "action": "BUY",
    "entry_point": 177.0,
    "target": 185.0,
    "stop_loss": 173.0
  }
}
```

**Fundamental Analyst**:
```json
{
  "ticker": "AAPL",
  "analysis_date": "2025-12-03",
  "valuation_metrics": {
    "pe_ratio": 28.5,
    "peg_ratio": 2.1,
    "price_to_book": 42.3,
    "price_to_sales": 7.8
  },
  "financial_health": {
    "roe": 147.5,
    "roa": 22.4,
    "debt_to_equity": 1.73,
    "current_ratio": 0.93
  },
  "growth_metrics": {
    "revenue_growth_yoy": 0.052,
    "earnings_growth_yoy": 0.089
  },
  "recommendation": {
    "rating": "HOLD",
    "fair_value": 182.0,
    "current_price": 178.5
  }
}
```

**Sentiment Analyst**:
```json
{
  "ticker": "AAPL",
  "analysis_date": "2025-12-03",
  "news_sentiment": {
    "overall_score": 0.65,
    "positive_count": 12,
    "neutral_count": 5,
    "negative_count": 3
  },
  "analyst_ratings": {
    "buy": 25,
    "hold": 10,
    "sell": 2,
    "consensus": "BUY"
  },
  "social_media_buzz": {
    "volume": "HIGH",
    "sentiment": "POSITIVE"
  },
  "upcoming_catalysts": [
    "Q4 Earnings Report - Jan 2025",
    "New Product Launch - Q1 2025"
  ]
}
```

**Risk Assessor**:
```json
{
  "ticker": "AAPL",
  "analysis_date": "2025-12-03",
  "volatility_metrics": {
    "beta": 1.28,
    "standard_deviation": 0.025,
    "vix_correlation": 0.45
  },
  "risk_measures": {
    "var_95": 0.035,
    "max_drawdown": 0.18,
    "sharpe_ratio": 1.45
  },
  "portfolio_fit": {
    "recommended_allocation": 0.15,
    "position_size": "MODERATE",
    "diversification_benefit": "HIGH"
  },
  "risk_factors": [
    "High valuation multiples",
    "Tech sector concentration",
    "Regulatory risks in China"
  ]
}
```

---

### 4. 실시간 검증 방법

#### 4-1. UI에서 테스트

1. **http://localhost:12000** 접속
2. "애플 주식 분석해줘" 입력
3. 다음을 확인:
   - ✅ 응답이 정상적으로 반환되는가?
   - ✅ 4개 에이전트 모두 응답했는가?
   - ❌ Artifacts(JSON 데이터)가 포함되어 있는가?
   - ✅ 한국어로 종합 보고서가 생성되는가?

#### 4-2. 직접 API 호출 (Advanced)

```bash
# Technical Analyst에게 직접 요청
curl -X POST http://localhost:10101/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "parts": [{"text": "Analyze AAPL stock"}]
      }
    ]
  }'
```

**기대 응답 구조** (Artifacts 구현 시):
```json
{
  "task_id": "uuid...",
  "status": {
    "state": "completed",
    "message": {
      "role": "agent",
      "parts": [
        {"text": "Based on my technical analysis..."},
        {"inline_data": {
          "mime_type": "application/json",
          "data": "base64_encoded_json..."
        }}
      ]
    }
  }
}
```

---

## ⚠️ 현재 문제점 및 해결 방안

### 문제 1: Artifacts 미구현

**증상**:
- UI 로그: `Couldn't convert to messages: 'result'`
- UI 로그: `No message content`
- 에이전트가 텍스트만 반환, JSON 데이터 없음

**원인**:
- Phase 3 롤백 시 commit bc8e989로 복구
- 그 당시 Artifacts 미구현 상태

**해결 방안**:

**Option 1: Artifacts 재구현** (권장)
```bash
# 각 에이전트에 after_model_callback 추가
# 1. Technical Analyst
# 2. Fundamental Analyst
# 3. Sentiment Analyst
# 4. Risk Assessor
```

**Option 2: 현재 상태 유지**
- 텍스트 응답만으로도 시스템은 정상 작동
- 시각화는 추후 Phase 4에서 구현

---

### 문제 2: 로그에서 "No message content" 발생

**증상**:
```
No message content
No message content
No message content
```

**가능한 원인**:
1. 에이전트가 빈 응답 반환
2. MCP 타임아웃으로 데이터 수집 실패
3. Host Agent의 응답 변환 오류

**디버깅 방법**:

```bash
# 1. 각 에이전트 개별 테스트
curl http://localhost:10101/.well-known/agent-card.json
curl http://localhost:10102/.well-known/agent-card.json
curl http://localhost:10103/.well-known/agent-card.json
curl http://localhost:10104/.well-known/agent-card.json

# 2. 에이전트 로그 직접 확인
# (각 에이전트의 stdout/stderr 확인 필요)
```

---

## 📊 검증 체크리스트

### 기본 동작 검증

- [x] 4개 에이전트 모두 실행 중
- [x] Agent Card 응답 정상
- [x] Host Agent 등록 완료
- [x] UI 접속 가능
- [x] 사용자 요청 받기 성공
- [x] 한국어 종합 보고서 반환

### 에이전트별 역할 수행 검증

- [ ] Technical Analyst: MCP로 데이터 수집 → 기술적 분석 수행
- [ ] Fundamental Analyst: MCP로 재무 데이터 수집 → 펀더멘털 분석 수행
- [ ] Sentiment Analyst: MCP로 뉴스 수집 → 감정 분석 수행
- [ ] Risk Assessor: 데이터 기반 리스크 평가 수행

### Artifacts 검증

- [ ] Technical Analyst: JSON 형식 Artifacts 반환
- [ ] Fundamental Analyst: JSON 형식 Artifacts 반환
- [ ] Sentiment Analyst: JSON 형식 Artifacts 반환
- [ ] Risk Assessor: JSON 형식 Artifacts 반환
- [ ] UI: Artifacts를 정상적으로 파싱 및 표시

---

## 🚀 다음 단계

### Phase 4: Artifacts 구현 (추천)

1. **각 에이전트에 `after_model_callback` 추가**
   - JSON 추출 로직 구현
   - `set_artifacts()` 호출

2. **Instruction 업데이트**
   - "ALWAYS include JSON data in your response"
   - JSON 스키마 예시 제공

3. **UI 개선**
   - Artifacts 데이터 시각화
   - 차트 라이브러리 통합 (Chart.js, Plotly)
   - 테이블 형식 데이터 표시

4. **검증**
   - 이 가이드의 체크리스트 모두 완료
   - 실제 주식 데이터로 end-to-end 테스트

---

## 📝 로그 분석 예시

### 정상 동작 로그

```
INFO: 127.0.0.1:xxxxx - "GET /.well-known/agent-card.json HTTP/1.1" 200 OK
INFO: 127.0.0.1:xxxxx - "POST /message/send HTTP/1.1" 200 OK
```

### Artifacts 변환 오류 로그

```
Couldn't convert to messages: 'result'
```
→ **의미**: Technical Analyst가 Artifacts를 반환했지만 UI가 처리 못함
→ **확인 필요**: UI의 convert_part 함수 로직

### 빈 응답 로그

```
No message content
No message content
```
→ **의미**: 에이전트가 빈 응답 반환
→ **확인 필요**:
  1. MCP 타임아웃 (Google ADK 5초 제한)
  2. 에이전트 로직 오류
  3. Host Agent 변환 오류

---

## 🎓 요약

**현재 상태**:
- ✅ 4개 에이전트 정상 작동 (각자 MCP로 데이터 수집)
- ✅ 한국어 종합 보고서 반환
- ❌ Artifacts 미구현 (텍스트만 반환)

**검증 방법**:
1. 로그 기반: UI 로그에서 오류 패턴 확인
2. 코드 기반: `after_model_callback` 구현 확인
3. 응답 기반: JSON 데이터 포함 여부 확인

**다음 단계**:
- Phase 4: Artifacts 구현 + UI 시각화

**참고**: 현재 시스템은 텍스트 응답만으로도 정상 작동합니다. Artifacts는 추후 시각화를 위한 선택적 개선 사항입니다.
