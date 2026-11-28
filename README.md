# A2A 주식 분석 에이전트: 이전 개발 작업 복원

보관 전용. 기존 공개 main은 포트폴리오이고, 4개 분석 에이전트와 데모 구현은 SungKong00/a2a_finance_project의 debug-infinite-loading에 있다. 각 파일은 별개의 시점을 복구하는 패치다. 연달아 적용하지 않는다.

| 패치 | 원본 코드에서 선택할 기준 | 보관 내용 |
|---|---|---|
| current-demo-ui.patch | f2d3fffd1211459df9191cfff2e3f5de7a4d8ae2 | 대화와 요약 UI, AVGO·CRWV 저장 응답 |
| old-main.patch | bases.txt의 old-main 기준 | 분석가 4개와 호스트의 초창기 작업 |
| early-optimization.patch | bases.txt의 early-optimization 기준 | 오래된 분석 최적화 코드와 설계 |
| ui-redesign-notes.patch | bases.txt의 ui-redesign-notes 기준 | UI 재설계 및 최적화 문서 |

공개 원본을 새로 전체 clone하고 기준 커밋을 체크아웃한다. 이 보관 브랜치를 받은 경로에서 패치 하나를 골라 git apply --check, git apply 순서로 적용한다. bases.txt에는 각각 기준과 원래 로컬 작업 끝 커밋이 있다. 원래 커밋 경계와 기타 로컬 이력은 맥의 A2A 보관 폴더에 있다. stash, 실제 환경값, 키는 이 원격에 없다.

검증 시 저장 응답 AVGO JSON에서 네 분석가를 확인할 수 있다. 실제 Google 키와 시장 데이터 연동은 별개다. 실행 호스트는 저장 응답이 없으면 외부 호출로 전환할 수 있으니, 재현 단계에는 키와 외부 연결을 넣지 않는다. 전체 분석 화면을 새로 실행했다는 뜻은 아니다.

current-demo-ui.patch를 적용한 뒤에만 demo-extra-files/ 아래 상대 경로를 복사한다. 추가 파일은 4종목의 데모 JSON 20개와 데모 CSS 1개다. 이전 역사 패치에는 복사하지 않는다.
