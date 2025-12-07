"""
Stock Input Component

A specialized input component for stock analysis that:
- Accepts only stock ticker or company name
- Auto-generates "XX 주식 분석해줘" request
- Shows recent search history as clickable chips
- [DEV] Mock button to test UI without API calls
"""

import uuid

import mesop as me

from a2a.types import Message, Part, Role, TextPart
from state.host_agent_service import (
    ListConversations,
    SendMessage,
    convert_message_to_state,
)
from state.state import AppState, StockAnalysis
from styles.stock_styles import (
    COLORS,
    HINT_TEXT_STYLE,
    RECENT_SEARCHES_STYLE,
    SEARCH_CHIP_STYLE,
    STOCK_INPUT_BUTTON_STYLE,
    STOCK_INPUT_CONTAINER_STYLE,
    STOCK_INPUT_FIELD_STYLE,
    STOCK_INPUT_ROW_STYLE,
)


MAX_RECENT_SEARCHES = 5


# =============================================================================
# MOCK DATA - 실제 API 응답 기반 테스트 데이터 (CoreWeave - CRWV)
# =============================================================================

# Mock data matching actual AI response structure
# Each agent returns JSON with specific marker fields for identification
MOCK_CRWV_DATA = {
    "ticker": "CRWV",
    "company_name": "CoreWeave, Inc.",
    # Technical: markers = rsi, macd_signal, support_levels, resistance_levels
    "technical": {
        "ticker": "CRWV",
        "current_price": 88.3,
        "trend": "강세",
        "rsi": None,
        "macd_signal": "강세",
        "support_levels": [33.52, 40.0, 51.57, 84.62],
        "resistance_levels": [150.0, 170.0, 187.0],
        "analysis_content": "## 기술적 분석: CoreWeave, Inc. (CRWV)\n\n### 추세 분석\n**현재 추세:** 강세\n\nCRWV는 2025년 3월 IPO 이후 강한 상승 추세를 보여왔습니다. 상당한 변동성에도 불구하고 전반적으로 상승 방향을 유지하며, 초기 거래가 대비 크게 상승했습니다.\n\n### 모멘텀 지표\n- **MACD**: 긍정적 영역에 있으며 강한 매수세를 나타냄\n- **RSI**: 급격한 가격 상승으로 과매수 영역 진입 가능성\n\n### 지지/저항선\n- **지지선**: $33.52 (52주 최저), $40.00, $51.57, $84.62\n- **저항선**: $150.00, $170.00, $187.00 (사상 최고가)"
    },
    # Fundamental: markers = pe_ratio, pb_ratio, roe, valuation_verdict, revenue_growth, market_cap
    "fundamental": {
        "ticker": "CRWV",
        "market_cap": 44001435648,
        "pe_ratio": -53.19,
        "pb_ratio": 11.33,
        "revenue_growth": 133.7,
        "roe": -29.17,
        "valuation_verdict": "고평가",
        "recommendation": "매수",
        "analysis_content": "## 펀더멘털 분석: CoreWeave, Inc. (CRWV)\n\n### 회사 개요\nCoreWeave는 생성형 AI(GenAI) 워크로드를 위한 클라우드 플랫폼을 운영합니다. GPU/CPU 컴퓨팅, 스토리지, 네트워킹 서비스를 제공하며 881명의 직원을 보유하고 있습니다.\n\n### 밸류에이션\n- **시가총액**: $440억\n- **P/E (후행)**: -53.19 (적자 기업)\n- **P/B**: 11.33 (높은 프리미엄)\n- **P/S**: 10.22\n- **애널리스트 목표가**: $132.2 (현재가 대비 50% 상승 여력)\n\n### 재무 건전성\n- **유동비율**: 0.487 (단기 유동성 우려)\n- **부채비율**: 485% (매우 높은 레버리지)\n- **총 부채**: $188억 / **총 현금**: $19억\n\n### 성장성\n- **매출 성장률**: 133.7% (폭발적 성장)\n- **EBITDA 마진**: 50.72%\n- **매출총이익률**: 73.85%\n\n### 결론\nCoreWeave는 AI 인프라 시장에서 높은 성장을 보이지만, 현재 적자 상태이며 높은 부채를 보유하고 있습니다. 고위험 고수익 투자입니다."
    },
    # Sentiment: markers = sentiment_score, sentiment_verdict, analyst_consensus, top_headlines
    "sentiment": {
        "ticker": "CRWV",
        "sentiment_score": 0.75,
        "sentiment_verdict": "강세",
        "analyst_consensus": "매수",
        "top_headlines": [
            "CoreWeave, 흑자 전환 성공 - Applied Digital과 대조적",
            "CoreWeave (CRWV), 새로운 AI 투자로 20.8% 급등",
            "연방 시장 진출로 CoreWeave 경쟁력 강화 전망"
        ],
        "analysis_content": "## 감성 분석: CoreWeave, Inc. (CRWV)\n\n**분석일**: 2025년 12월 7일\n**현재가**: $88.30\n\n### 뉴스 감성\n최근 CoreWeave 관련 뉴스는 압도적으로 긍정적입니다. AI 섹터에서의 성과와 전략적 성장에 초점을 맞추고 있으며, 최근 흑자 전환과 상당한 매출 성장이 주목받고 있습니다.\n\n### 애널리스트 평가\n- **평균 등급**: 2.1 - 매수\n- **목표가 범위**: $36 ~ $208\n- **평균 목표가**: $132.2\n\n### 시장 분위기\nAI 인프라 기업에 대한 시장 심리가 강하며, CoreWeave는 이 트렌드의 수혜자입니다. 주요 촉매제로는 흑자 전환, 연방 시장 진출, AI 기술 지속 투자 등이 있습니다."
    },
    # Risk: markers = risk_level, beta, sharpe_ratio, volatility, max_drawdown
    "risk": {
        "ticker": "CRWV",
        "risk_level": "매우 높음",
        "beta": 0.0,
        "volatility": 142.55,
        "max_drawdown": -62.3,
        "sharpe_ratio": 3.63,
        "analysis_content": "## 리스크 평가: CoreWeave, Inc. (CRWV)\n\n### 전체 리스크 수준: 매우 높음\n\n### 1. 변동성\n- **연간 변동성**: 142.55%\n- 극도로 높은 가격 변동을 보이며, 일일 큰 폭의 등락이 발생합니다.\n\n### 2. 시장 리스크 (베타)\n- **베타**: 측정 불가 (IPO 후 짧은 기간)\n- 시장 상관관계 데이터 부족\n\n### 3. 하방 리스크\n- **최대 낙폭**: -62.30%\n- 고점에서 매수 후 저점에서 매도 시 62% 이상 손실 가능\n\n### 4. 위험조정 수익률\n- **샤프 비율**: 3.63\n- 높은 수익률 대비 위험도 반영, 단 지속 가능성은 불확실\n\n### 결론\nCRWV는 극도로 투기적인 투자 대상입니다. 높은 변동성과 큰 낙폭 가능성으로 인해 고위험 감내 투자자에게만 적합합니다."
    },
    "recommendation": "매수",
    "summary": "CoreWeave(CRWV)는 AI 인프라 시장의 고성장 기업으로, 133.7%의 매출 성장을 기록했습니다. 강세 추세와 긍정적 시장 심리를 보이지만, 142.55%의 극심한 변동성과 62.3%의 최대 낙폭으로 매우 높은 리스크를 동반합니다. 고위험 감내 투자자에게 적합한 투기적 매수 기회입니다.",
    "confidence": 70.0
}


def on_stock_input_blur(e: me.InputBlurEvent):
    """Handle input blur - save value to state."""
    state = me.state(AppState)
    state.stock_input_value = e.value


async def _send_stock_analysis_request(ticker: str, conversation_id: str):
    """Send stock analysis request to the agent."""
    app_state = me.state(AppState)

    # Generate the analysis request message
    message_text = f"{ticker} 주식 분석해줘"

    # Reset current analysis and set loading state
    from state.state import StockAnalysis
    app_state.current_analysis = StockAnalysis(
        ticker=ticker.upper(),
        is_loading=True,
    )

    # Add to recent searches
    if ticker and ticker not in app_state.recent_searches:
        app_state.recent_searches.insert(0, ticker.upper())
        # Keep only last N searches
        app_state.recent_searches = app_state.recent_searches[:MAX_RECENT_SEARCHES]

    # Find the conversation
    conversations = await ListConversations()
    c = next(
        (x for x in conversations if x.conversation_id == conversation_id),
        None,
    )

    if not c:
        print(f'Conversation id {conversation_id} not found')
        return

    # Create and send the message
    message_id = str(uuid.uuid4())
    request = Message(
        message_id=message_id,
        context_id=conversation_id,
        role=Role.user,
        parts=[Part(root=TextPart(text=message_text))],
    )

    # Add message to state
    state_message = convert_message_to_state(request)
    if not app_state.messages:
        app_state.messages = []
    app_state.messages.append(state_message)

    # Update conversation
    conversation = next(
        filter(
            lambda x: c and x.conversation_id == c.conversation_id,
            app_state.conversations,
        ),
        None,
    )
    if conversation:
        conversation.message_ids.append(state_message.message_id)

    # Track background task
    app_state.background_tasks[message_id] = ''

    # Send the message
    await SendMessage(request)

    # Clear input
    app_state.stock_input_value = ''


async def on_stock_input_enter(e: me.InputEnterEvent):
    """Handle Enter key - send analysis request."""
    yield
    app_state = me.state(AppState)
    ticker = e.value.strip()

    if not ticker:
        return

    conversation_id = app_state.current_conversation_id
    if not conversation_id:
        print('No conversation selected')
        return

    yield
    await _send_stock_analysis_request(ticker, conversation_id)
    yield


async def on_analyze_button_click(e: me.ClickEvent):
    """Handle analyze button click."""
    yield
    app_state = me.state(AppState)
    ticker = app_state.stock_input_value.strip()

    if not ticker:
        return

    conversation_id = app_state.current_conversation_id
    if not conversation_id:
        print('No conversation selected')
        return

    yield
    await _send_stock_analysis_request(ticker, conversation_id)
    yield


async def on_chip_click(e: me.ClickEvent):
    """Handle recent search chip click - re-analyze that ticker."""
    yield
    app_state = me.state(AppState)
    ticker = e.key

    if not ticker:
        return

    conversation_id = app_state.current_conversation_id
    if not conversation_id:
        print('No conversation selected')
        return

    yield
    await _send_stock_analysis_request(ticker, conversation_id)
    yield


def on_mock_button_click(e: me.ClickEvent):
    """[DEV] Load mock data directly without API call."""
    app_state = me.state(AppState)

    # Use CRWV mock data
    mock_data = MOCK_CRWV_DATA

    # Set the analysis state directly
    app_state.current_analysis = StockAnalysis(
        ticker=mock_data["ticker"],
        company_name=mock_data.get("company_name", ""),
        technical=mock_data.get("technical", {}),
        fundamental=mock_data.get("fundamental", {}),
        sentiment=mock_data.get("sentiment", {}),
        risk=mock_data.get("risk", {}),
        recommendation=mock_data.get("recommendation", ""),
        summary=mock_data.get("summary", ""),
        confidence=mock_data.get("confidence", 0),
        is_loading=False,
        error="",
    )

    print("[MOCK] Loaded mock data for CRWV")


@me.component
def recent_search_chip(ticker: str):
    """Render a clickable chip for recent search."""
    with me.box(
        key=ticker,
        style=SEARCH_CHIP_STYLE,
        on_click=on_chip_click,
    ):
        me.text(ticker)


@me.component
def stock_input():
    """
    Stock-specific input component.

    Features:
    - Clean input field for ticker/company name
    - Analyze button
    - Hint text with examples
    - Recent search history as chips
    - [DEV] Mock button for UI testing
    """
    app_state = me.state(AppState)

    with me.box(style=STOCK_INPUT_CONTAINER_STYLE):
        # Input row
        with me.box(style=STOCK_INPUT_ROW_STYLE):
            me.input(
                label='종목명 또는 티커 입력',
                value=app_state.stock_input_value,
                on_blur=on_stock_input_blur,
                on_enter=on_stock_input_enter,
                style=STOCK_INPUT_FIELD_STYLE,
            )
            me.button(
                label='분석',
                type='flat',
                color='primary',
                on_click=on_analyze_button_click,
                style=STOCK_INPUT_BUTTON_STYLE,
            )
            # [DEV] Mock button - API 호출 없이 테스트
            me.button(
                label='Mock (CRWV)',
                type='stroked',
                color='warn',
                on_click=on_mock_button_click,
                style=me.Style(
                    flex_shrink=0,
                    margin=me.Margin(left=8),
                ),
            )

        # Hint text
        with me.box(style=HINT_TEXT_STYLE):
            me.text('예시: AAPL, TSLA, NVDA, 005930.KS, 삼성전자, 테슬라')

        # Recent searches
        if app_state.recent_searches:
            with me.box(style=me.Style(margin=me.Margin(top=12))):
                me.text(
                    '최근 검색:',
                    style=me.Style(
                        font_size=13,
                        color=COLORS['text_secondary'],
                        margin=me.Margin(bottom=8),
                    ),
                )
                with me.box(style=RECENT_SEARCHES_STYLE):
                    for ticker in app_state.recent_searches:
                        recent_search_chip(ticker)
