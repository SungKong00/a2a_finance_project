# 📚 Study Archive

이 디렉토리는 프로젝트 개발 과정에서 학습한 내용과 아키텍처 분석을 정리한 공간입니다.

---

## 📖 문서 목록

### 1. [Multi-Agent Architecture Patterns](./01_MULTI_AGENT_ARCHITECTURE_PATTERNS.md)
**주제**: 멀티 에이전트 시스템 설계 패턴 완벽 가이드

**다루는 내용**:
- 4가지 주요 멀티 에이전트 설계 패턴
  - Hierarchical Task Decomposition
  - Orchestrator-Worker Pattern
  - Multi-Agent Parallel Pattern
  - Event-Driven Pattern
- 금융 분석 시스템의 올바른 3-Layer 아키텍처
- 실제 사례 연구 (Schroders, Anthropic)
- 핵심 설계 원칙 및 안티패턴
- 워크플로우 예시 및 코드 샘플

**핵심 교훈**:
> "정보 수집, 분석, 종합을 분리하라"

**추천 대상**: 멀티 에이전트 시스템 설계를 처음 배우는 사람

**예상 학습 시간**: 45-60분

---

### 2. [Current Architecture Analysis](./02_CURRENT_ARCHITECTURE_ANALYSIS.md)
**주제**: 현재 프로젝트 아키텍처 분석 및 문제점 정리

**다루는 내용**:
- 현재 구현 상태 상세 분석
- 발견된 4가지 주요 문제점
  - 포트 충돌 (Stock Analyst vs Technical Analyst)
  - Stock Analyst 역할 불명확
  - 아키텍처 레이어 불일치
  - 종합 에이전트 부재
- 설계 vs 구현 비교표 (일치도 60%)
- 3가지 수정 방안 (Option 1, 2, 3)
- 마이그레이션 계획 및 검증 방법

**핵심 발견**:
- 분석 에이전트가 MCP에 직접 연결 (잘못됨)
- 데이터 수집과 분석이 혼재
- 중복 요청 발생 (4개 에이전트가 각각 요청)

**추천 대상**: 프로젝트 리팩토링 전에 읽어야 함

**예상 학습 시간**: 30-45분

---

## 🎯 학습 경로

### **초보자를 위한 순서**
1. 먼저 **01_MULTI_AGENT_ARCHITECTURE_PATTERNS.md** 읽기
   - 멀티 에이전트 시스템 기본 개념 이해
   - 4가지 주요 패턴 숙지
   - 올바른 아키텍처 이해

2. 다음 **02_CURRENT_ARCHITECTURE_ANALYSIS.md** 읽기
   - 현재 프로젝트 문제점 파악
   - 수정 방안 검토
   - 마이그레이션 계획 이해

3. 실제 코드 리뷰
   - `agents/*/agent.py` 파일들 분석
   - 문서와 코드 비교하며 이해

### **경험자를 위한 순서**
1. **02_CURRENT_ARCHITECTURE_ANALYSIS.md** 먼저 읽고 문제점 파악
2. **01_MULTI_AGENT_ARCHITECTURE_PATTERNS.md** 참고하여 해결책 구상
3. 직접 리팩토링 계획 수립

---

## 🔑 핵심 Takeaways

### **멀티 에이전트 설계의 골든 룰**

1. **Separation of Concerns** (관심사의 분리)
   ```
   수집 에이전트 → 데이터 수집만
   분석 에이전트 → 분석만
   종합 에이전트 → 종합만
   ```

2. **Single Source of Truth** (단일 진실 공급원)
   ```
   데이터는 한 곳에서만 수집
   모든 에이전트가 같은 데이터 사용
   ```

3. **Unidirectional Data Flow** (단방향 데이터 흐름)
   ```
   수집 → 분석 → 종합 (역방향 금지)
   ```

4. **Orchestration over Choreography** (조율 > 안무)
   ```
   중앙 조율자가 워크플로우 관리
   에이전트끼리 직접 통신 지양
   ```

5. **Parallel When Possible** (가능하면 병렬)
   ```
   독립적인 작업은 병렬 실행
   의존성 있는 작업만 순차 실행
   ```

---

## 🏗️ 올바른 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────┐
│  User Interface (Mesop UI)                      │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────┐
│  Host Agent (Orchestrator)                      │
│  - 전체 작업 흐름 관리                           │
│  - Layer 간 조율                                │
└────────────────────┬────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ↓                ↓                ↓
┌─────────┐    ┌─────────┐    ┌─────────┐
│ Layer 1 │    │ Layer 2 │    │ Layer 3 │
│  수집   │ →  │  분석   │ →  │  종합   │
└─────────┘    └─────────┘    └─────────┘

Layer 1: Data Collection
- Market Data Collector
- News Collector
- Financial Collector

Layer 2: Analysis
- Technical Analyst
- Fundamental Analyst
- Sentiment Analyst
- Risk Assessor

Layer 3: Synthesis
- Investment Advisor
- Report Generator
```

---

## 📚 추천 외부 자료

### **공식 문서**
1. [Google Cloud: Agentic AI Design Patterns](https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system)
2. [Microsoft Azure: AI Agent Orchestration](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
3. [Anthropic: Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)

### **실무 가이드**
4. [A2A Protocol Enterprise Guide](https://www.kenility.com/blog/ai-tech-innovations/google-a2a-protocol-guide-ultimate-ai-agent-orchestration-strategy)
5. [Financial Analysis Multi-Agent Systems](https://medium.com/@batuhansenerr/ai-powered-financial-analysis-multi-agent-systems-transform-data-into-insights-d94e4867d75d)

### **케이스 스터디**
6. [Schroders Multi-Agent Assistant](https://cloud.google.com/blog/topics/customers/how-schroders-built-its-multi-agent-financial-analysis-research-assistant)
7. [AWS Financial Assistant](https://aws.amazon.com/blogs/machine-learning/build-a-gen-ai-powered-financial-assistant-with-amazon-bedrock-multi-agent-collaboration/)

---

## 🎓 자가 평가 체크리스트

학습 후 스스로 확인해보세요:

### **기본 개념**
- [ ] 멀티 에이전트 시스템이란 무엇인가?
- [ ] 왜 단일 에이전트보다 멀티 에이전트가 나은가?
- [ ] 4가지 주요 패턴의 차이점을 설명할 수 있는가?

### **설계 원칙**
- [ ] "Separation of Concerns"를 실제 코드로 구현할 수 있는가?
- [ ] 데이터 수집과 분석을 분리해야 하는 이유를 설명할 수 있는가?
- [ ] Orchestrator-Worker 패턴의 장단점을 나열할 수 있는가?

### **실무 적용**
- [ ] 금융 분석 시스템에 3-Layer 아키텍처가 필요한 이유를 설명할 수 있는가?
- [ ] 현재 프로젝트의 4가지 문제점을 설명할 수 있는가?
- [ ] 3가지 수정 방안 중 어떤 것이 최선인지 판단할 수 있는가?

### **고급 주제**
- [ ] 병렬 실행 vs 순차 실행 판단 기준을 설명할 수 있는가?
- [ ] 에이전트 간 데이터 전달 방식을 설계할 수 있는가?
- [ ] 에러 처리 및 재시도 로직을 어디에 구현해야 하는가?

---

## 🔄 문서 업데이트 이력

| 날짜 | 문서 | 변경 사항 |
|------|------|----------|
| 2025-12-03 | 01_MULTI_AGENT_ARCHITECTURE_PATTERNS.md | 초안 작성 |
| 2025-12-03 | 02_CURRENT_ARCHITECTURE_ANALYSIS.md | 초안 작성 |
| 2025-12-03 | README.md | 초안 작성 |

---

## 💬 피드백 및 질문

이 스터디 자료에 대한 질문이나 개선 사항이 있다면:
1. 프로젝트 디렉토리에 메모 남기기
2. 관련 이슈 생성
3. 문서 직접 수정 후 커밋

---

## 🎯 다음 학습 주제

- [ ] A2A 프로토콜 상세 분석
- [ ] MCP 서버 구현 방법
- [ ] 에이전트 간 통신 최적화
- [ ] 에러 처리 및 복원력(Resilience) 패턴
- [ ] 성능 모니터링 및 로깅
- [ ] 프로덕션 배포 전략

---

**마지막 업데이트**: 2025-12-03
**유지 관리자**: 프로젝트 팀
**라이선스**: 내부 학습 자료
