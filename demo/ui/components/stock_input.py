import mesop as me
import uuid

from a2a.types import Message, Part, Role, TextPart
from state.state import AppState, StockAnalysis
from state.host_agent_service import CreateConversation, SendMessage
from styles.stock_styles import (
    STOCK_INPUT_CONTAINER_STYLE,
    STOCK_INPUT_ROW_STYLE,
    STOCK_INPUT_FIELD_STYLE,
    STOCK_INPUT_BUTTON_STYLE,
    RECENT_SEARCHES_STYLE,
    SEARCH_CHIP_STYLE,
    SEARCH_CHIP_HOVER_STYLE,
    HINT_TEXT_STYLE,
    COLORS,
)


def on_stock_input_blur(e: me.InputBlurEvent):
    """Handle stock input blur event."""
    state = me.state(AppState)
    state.stock_input_value = e.value


async def on_stock_input_enter(e: me.InputEnterEvent):
    """Handle Enter key in stock input."""
    state = me.state(AppState)
    state.stock_input_value = e.value
    if state.stock_input_value.strip():
        await _trigger_analysis(state, state.stock_input_value.strip())


async def on_analyze_button_click(e: me.ClickEvent):
    """Handle analyze button click."""
    state = me.state(AppState)
    ticker = state.stock_input_value.strip()
    if ticker:
        await _trigger_analysis(state, ticker)


async def on_chip_click(e: me.ClickEvent):
    """Handle click on recent search chip."""
    state = me.state(AppState)
    ticker = e.key
    state.stock_input_value = ticker
    await _trigger_analysis(state, ticker)


async def on_mock_button_click(e: me.ClickEvent):
    """[DEV] Mock button click handler."""
    state = me.state(AppState)
    ticker = "CRWV"
    state.stock_input_value = ticker
    await _trigger_analysis(state, ticker)


async def _trigger_analysis(state: AppState, ticker: str):
    """Trigger stock analysis for the given ticker."""
    # Reset current analysis
    state.current_analysis = StockAnalysis(
        ticker=ticker.upper(),
        is_loading=True,
        technical_done=False,
        fundamental_done=False,
        sentiment_done=False,
        risk_done=False,
    )

    # Add to recent searches
    ticker_upper = ticker.upper()
    if ticker_upper in state.recent_searches:
        state.recent_searches.remove(ticker_upper)
    state.recent_searches.insert(0, ticker_upper)
    state.recent_searches = state.recent_searches[:10]

    # Create or use conversation
    if not state.current_conversation_id:
        conversation = await CreateConversation()
        state.current_conversation_id = conversation.conversation_id

    # Send message to agents
    message_id = str(uuid.uuid4())
    request = Message(
        message_id=message_id,
        context_id=state.current_conversation_id,
        role=Role.user,
        parts=[Part(root=TextPart(text=f"{ticker_upper} 주식을 분석해줘"))],
    )
    state.background_tasks[message_id] = ''
    await SendMessage(request)


def recent_search_chip(ticker: str):
    """Render a single recent search chip."""
    with me.box(
        key=ticker,
        on_click=on_chip_click,
        style=SEARCH_CHIP_STYLE,
    ):
        me.text(ticker)


@me.component
def stock_input():
    """
    Stock-specific input component (full version for empty state).

    Features:
    - Clean input field for ticker/company name
    - Analyze button
    - Hint text with examples
    - Recent search history as chips
    """
    app_state = me.state(AppState)

    with me.box(style=STOCK_INPUT_CONTAINER_STYLE):
        # 한 줄에 모든 요소 배치: 입력창 + 버튼 + 힌트
        with me.box(style=STOCK_INPUT_ROW_STYLE):
            me.input(
                placeholder='종목명 또는 티커 (예: AAPL, 삼성전자)',
                value=app_state.stock_input_value,
                on_blur=on_stock_input_blur,
                on_enter=on_stock_input_enter,
                appearance='outline',
                subscript_sizing='dynamic',
                style=STOCK_INPUT_FIELD_STYLE,
            )
            me.button(
                label='분석하기',
                type='flat',
                color='primary',
                on_click=on_analyze_button_click,
                style=STOCK_INPUT_BUTTON_STYLE,
            )

        # Recent searches
        if app_state.recent_searches:
            with me.box(style=me.Style(margin=me.Margin(top=12))):
                me.text('최근 검색:', style=me.Style(
                    font_size=12,
                    color=COLORS['text_secondary'],
                    margin=me.Margin(bottom=4),
                ))
                with me.box(style=RECENT_SEARCHES_STYLE):
                    for ticker in app_state.recent_searches:
                        recent_search_chip(ticker)


@me.component
def compact_stock_input():
    """
    Compact stock input for top bar - modern dark theme style.
    """
    app_state = me.state(AppState)

    # Container style - minimal top bar
    container_style = me.Style(
        display='flex',
        flex_direction='row',
        align_items='center',
        gap=12,
        padding=me.Padding(top=12, bottom=12, left=20, right=20),
        background=COLORS['surface'],
        border=me.Border(
            bottom=me.BorderSide(width=1, color=COLORS['card_border'], style='solid')
        ),
    )

    with me.box(style=container_style):
        # Search input with icon
        me.input(
            placeholder='종목명 또는 티커 (예: AAPL, 삼성전자)',
            value=app_state.stock_input_value,
            on_blur=on_stock_input_blur,
            on_enter=on_stock_input_enter,
            type='text',
            appearance='outline',
            subscript_sizing='dynamic',
            style=me.Style(
                flex_grow=1,
                max_width=400,
            ),
        )

        # Analyze button - modern style
        analyze_btn_style = me.Style(
            padding=me.Padding(top=10, bottom=10, left=18, right=18),
            background=COLORS['accent'],
            border_radius=8,
            cursor='pointer',
        )
        with me.box(style=analyze_btn_style, on_click=on_analyze_button_click):
            me.text('분석', style=me.Style(
                color='#FFFFFF',
                font_size=14,
                font_weight='600',
            ))

        # Mock button
        mock_btn_style = me.Style(
            display='flex',
            align_items='center',
            gap=4,
            padding=me.Padding(top=8, bottom=8, left=12, right=12),
            background='transparent',
            border=me.Border.all(me.BorderSide(width=1, color=COLORS['hold'], style='solid')),
            border_radius=6,
            cursor='pointer',
        )
        with me.box(style=mock_btn_style, on_click=on_mock_button_click):
            me.icon('science', style=me.Style(
                color=COLORS['hold'],
                font_size=16,
            ))
            me.text('Mock', style=me.Style(
                color=COLORS['hold'],
                font_size=12,
            ))

        # Recent searches as chips (if any)
        if app_state.recent_searches:
            with me.box(style=me.Style(
                display='flex',
                flex_direction='row',
                gap=8,
                margin=me.Margin(left=8),
            )):
                for ticker in app_state.recent_searches[:3]:
                    chip_style = me.Style(
                        padding=me.Padding(top=6, bottom=6, left=12, right=12),
                        background=COLORS['card_background'],
                        border=me.Border.all(
                            me.BorderSide(width=1, color=COLORS['card_border'], style='solid')
                        ),
                        border_radius=16,
                        cursor='pointer',
                    )
                    with me.box(key=ticker, style=chip_style, on_click=on_chip_click):
                        me.text(ticker, style=me.Style(
                            color=COLORS['text_secondary'],
                            font_size=13,
                        ))
