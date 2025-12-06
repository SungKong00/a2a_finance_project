"""
Stock Input Component

A specialized input component for stock analysis that:
- Accepts only stock ticker or company name
- Auto-generates "XX 주식 분석해줘" request
- Shows recent search history as clickable chips
"""

import uuid

import mesop as me

from a2a.types import Message, Part, Role, TextPart
from state.host_agent_service import (
    ListConversations,
    SendMessage,
    convert_message_to_state,
)
from state.state import AppState
from styles.stock_styles import (
    HINT_TEXT_STYLE,
    RECENT_SEARCHES_STYLE,
    SEARCH_CHIP_STYLE,
    STOCK_INPUT_BUTTON_STYLE,
    STOCK_INPUT_CONTAINER_STYLE,
    STOCK_INPUT_FIELD_STYLE,
    STOCK_INPUT_ROW_STYLE,
)


MAX_RECENT_SEARCHES = 5


def on_stock_input_blur(e: me.InputBlurEvent):
    """Handle input blur - save value to state."""
    state = me.state(AppState)
    state.stock_input_value = e.value


async def _send_stock_analysis_request(ticker: str, conversation_id: str):
    """Send stock analysis request to the agent."""
    app_state = me.state(AppState)

    # Generate the analysis request message
    message_text = f"{ticker} 주식 분석해줘"

    # Add to recent searches
    if ticker and ticker not in app_state.recent_searches:
        app_state.recent_searches.insert(0, ticker)
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
                        color='#757575',
                        margin=me.Margin(bottom=8),
                    ),
                )
                with me.box(style=RECENT_SEARCHES_STYLE):
                    for ticker in app_state.recent_searches:
                        recent_search_chip(ticker)
