import mesop as me
from typing import Dict, Any, List

from state.state import AppState
from styles.stock_styles import COLORS
from components.analysis_card import analysis_card
from components.summary_badge import summary_badge, summary_badge_row
from components.chart_components import confidence_gauge


def stock_dashboard(
    ticker: str,
    analysis_data: Dict[str, Any],
    expanded_cards: Dict[str, bool],
):
    """
    Render the main stock analysis dashboard.
    """
    app_state = me.state(AppState)

    # Main Container
    dashboard_style = me.Style(
        display='flex',
        flex_direction='column',
        gap=24,
        padding=me.Padding.all(24),
        background=COLORS['background'],
        min_height='100vh',
    )

    with me.box(style=dashboard_style):
        # 1. Header Section (Ticker, Price, Summary Badges)
        _render_dashboard_header(ticker, analysis_data)

        # 2. Recommendation & Confidence
        _render_recommendation_section(analysis_data)

        # 3. Analysis Cards Grid
        cards_grid_style = me.Style(
            display='grid',
            grid_template_columns='repeat(auto-fit, minmax(450px, 1fr))',
            gap=24,
        )

        with me.box(style=cards_grid_style):
            # Technical Analysis Card
            analysis_card(
                card_type='technical',
                data=analysis_data.get('technical') or {},
                expanded=expanded_cards.get('technical', False),
                on_expand_click=lambda e: _on_toggle_card(e, 'technical'),
            )

            # Fundamental Analysis Card
            analysis_card(
                card_type='fundamental',
                data=analysis_data.get('fundamental') or {},
                expanded=expanded_cards.get('fundamental', False),
                on_expand_click=lambda e: _on_toggle_card(e, 'fundamental'),
            )

            # Sentiment Analysis Card
            analysis_card(
                card_type='sentiment',
                data=analysis_data.get('sentiment') or {},
                expanded=expanded_cards.get('sentiment', False),
                on_expand_click=lambda e: _on_toggle_card(e, 'sentiment'),
            )

            # Risk Assessment Card
            analysis_card(
                card_type='risk',
                data=analysis_data.get('risk') or {},
                expanded=expanded_cards.get('risk', False),
                on_expand_click=lambda e: _on_toggle_card(e, 'risk'),
            )


def _on_toggle_card(e: me.ClickEvent, card_key: str):
    """Toggle card expansion state."""
    state = me.state(AppState)
    current = state.analysis_card_expanded.get(card_key, False)
    state.analysis_card_expanded[card_key] = not current


def _render_dashboard_header(ticker: str, data: Dict[str, Any]):
    """Render dashboard header with ticker and key badges."""
    header_style = me.Style(
        display='flex',
        justify_content='space-between',
        align_items='flex-start',
        flex_wrap='wrap',
        gap=20,
    )

    with me.box(style=header_style):
        # Left: Ticker & Name
        title_col = me.Style(display='flex', flex_direction='column')
        with me.box(style=title_col):
            me.text(ticker.upper(), style=me.Style(
                font_size=36,
                font_weight='800',
                color=COLORS['text_primary'],
                letter_spacing='1px',
            ))
            company_name = data.get('company_name') or 'Stock Analysis'
            me.text(company_name, style=me.Style(
                font_size=16,
                color=COLORS['text_secondary'],
                font_weight='500',
            ))

        # Right: Summary Badges
        _render_summary_section(data)


def _render_summary_section(data: Dict[str, Any]):
    """Render top-level summary badges based on agent verdicts."""
    badges = []

    if 'technical' in data and data['technical']:
        tech = data['technical']
        if tech.get('trend'):
            badges.append({'label': '추세', 'value': tech['trend']})

    if 'fundamental' in data and data['fundamental']:
        fund = data['fundamental']
        # Use valuation_verdict from schema
        valuation = fund.get('valuation_verdict') or fund.get('valuation')
        if valuation:
            badges.append({'label': '밸류에이션', 'value': valuation})

    if 'sentiment' in data and data['sentiment']:
        sent = data['sentiment']
        # Use sentiment_verdict from schema
        sentiment = sent.get('sentiment_verdict') or sent.get('sentiment')
        if sentiment:
            badges.append({'label': '시장 심리', 'value': sentiment})

    if 'risk' in data and data['risk']:
        risk = data['risk']
        if risk.get('risk_level'):
            badges.append({'label': '리스크', 'value': risk['risk_level']})

    # Add recommendation if available
    recommendation = data.get('recommendation') or data.get('final_recommendation')
    if recommendation:
        badges.append({'label': '투자 의견', 'value': recommendation})

    if badges:
        summary_badge_row(badges)


def _render_recommendation_section(data: Dict[str, Any]):
    """Render final recommendation and summary text."""
    recommendation = data.get('recommendation')
    summary = data.get('summary')
    confidence = data.get('confidence', 0.85)  # Default confidence if missing

    container_style = me.Style(
        background=COLORS['card_background'],
        border_radius=16,
        padding=me.Padding.all(24),
        border=me.Border.all(
            me.BorderSide(width=1, color=COLORS['card_border'], style='solid')
        ),
    )

    with me.box(style=container_style):
        header_style = me.Style(
            display='flex',
            align_items='center',
            gap=12,
            margin=me.Margin(bottom=16),
        )

        with me.box(style=header_style):
            me.icon('auto_awesome', style=me.Style(
                color=COLORS['accent'],
                font_size=24,
            ))
            me.text('종합 분석 요약', style=me.Style(
                font_size=18,
                font_weight='bold',
                color=COLORS['text_primary'],
            ))

        content_style = me.Style(
            display='flex',
            flex_direction='row',
            gap=32,
            flex_wrap='wrap',
            align_items='flex-start',
        )

        with me.box(style=content_style):
            # Left: Indicators
            indicators_style = me.Style(
                display='flex',
                flex_direction='column',
                gap=16,
                min_width=200,
            )
            with me.box(style=indicators_style):
                badge_container = me.Style(margin=me.Margin(bottom=8))
                
                if recommendation:
                    with me.box(style=badge_container):
                        summary_badge(
                            label='최종 투자 의견',
                            value=recommendation,
                        )

                # Confidence Gauge
                gauge_container = me.Style(
                    background=COLORS['surface'],
                    padding=me.Padding.all(16),
                    border_radius=12,
                    display='flex',
                    justify_content='center',
                )
                with me.box(style=gauge_container):
                    confidence_gauge(confidence, '분석 신뢰도')

            # Right: Summary Text
            if summary:
                text_container = me.Style(
                    flex_grow=1,
                    min_width=300,
                    background=COLORS['surface'],
                    padding=me.Padding.all(20),
                    border_radius=12,
                )
                with me.box(style=text_container):
                    me.text(summary, style=me.Style(
                        font_size=15,
                        line_height='1.7',
                        color=COLORS['text_primary'],
                    ))


def loading_dashboard(ticker: str = '', progress: dict = None):
    """
    Render loading state with progress indicators - modern style.
    """
    if progress is None:
        progress = {}

    container_style = me.Style(
        display='flex',
        flex_direction='column',
        align_items='center',
        justify_content='center',
        min_height=450,
        gap=28,
        padding=me.Padding.all(40),
        background=COLORS['background'],
    )

    with me.box(style=container_style):
        # Ticker display with modern styling
        if ticker:
            ticker_container = me.Style(
                display='flex',
                flex_direction='column',
                align_items='center',
                gap=8,
            )
            with me.box(style=ticker_container):
                me.text(ticker.upper(), style=me.Style(
                    font_size=36,
                    font_weight='800',
                    color=COLORS['text_primary'],
                    letter_spacing='2px',
                ))
                me.text('AI 분석 진행 중', style=me.Style(
                    font_size=14,
                    color=COLORS['accent'],
                    font_weight='500',
                ))

        # Modern spinner container
        spinner_container = me.Style(
            display='flex',
            align_items='center',
            justify_content='center',
            width=60,
            height=60,
            background=f'linear-gradient(135deg, {COLORS["accent"]}20 0%, {COLORS["accent"]}05 100%)',
            border_radius=16,
        )
        with me.box(style=spinner_container):
            me.progress_spinner()

        # Progress indicators for each agent
        agents = [
            ('technical', '기술적 분석', 'candlestick_chart', COLORS['buy']),
            ('fundamental', '펀더멘털 분석', 'account_balance', COLORS['bullish']),
            ('sentiment', '시장 심리', 'psychology', COLORS['hold']),
            ('risk', '리스크 평가', 'shield', COLORS['bearish']),
        ]

        progress_container = me.Style(
            display='flex',
            flex_direction='column',
            gap=10,
            width='100%',
            max_width=380,
        )

        with me.box(style=progress_container):
            for agent_key, agent_name, icon_name, agent_color in agents:
                is_done = progress.get(agent_key, False)
                _render_progress_item(agent_name, icon_name, is_done, agent_color)


def _render_progress_item(name: str, icon: str, is_done: bool, accent_color: str = None):
    """Render a single progress item with modern styling."""
    if accent_color is None:
        accent_color = COLORS['accent']

    done_color = COLORS['bullish']
    pending_color = COLORS['text_secondary']

    # Use accent color for pending, green for done
    item_color = done_color if is_done else accent_color
    text_color = done_color if is_done else COLORS['text_primary']
    icon_name = 'check_circle' if is_done else icon

    row_style = me.Style(
        display='flex',
        align_items='center',
        gap=14,
        padding=me.Padding(top=12, bottom=12, left=16, right=16),
        background=f'{item_color}08' if is_done else COLORS['card_background'],
        border_radius=12,
        border=me.Border.all(
            me.BorderSide(
                width=1,
                color=f'{item_color}40' if is_done else COLORS['card_border'],
                style='solid'
            )
        ),
    )

    with me.box(style=row_style):
        # Icon container
        icon_bg = me.Style(
            display='flex',
            align_items='center',
            justify_content='center',
            width=36,
            height=36,
            background=f'{item_color}20',
            border_radius=10,
        )
        with me.box(style=icon_bg):
            me.icon(icon_name, style=me.Style(
                font_size=18,
                color=item_color,
            ))

        # Name
        me.text(name, style=me.Style(
            font_size=14,
            color=text_color,
            flex_grow=1,
            font_weight='500',
        ))

        # Status badge
        if is_done:
            status_style = me.Style(
                display='flex',
                align_items='center',
                gap=4,
                padding=me.Padding(top=4, bottom=4, left=10, right=10),
                background=f'{done_color}20',
                border_radius=20,
            )
            with me.box(style=status_style):
                me.icon('check', style=me.Style(font_size=14, color=done_color))
                me.text('완료', style=me.Style(
                    font_size=12,
                    color=done_color,
                    font_weight='600',
                ))
        else:
            status_style = me.Style(
                display='flex',
                align_items='center',
                gap=4,
                padding=me.Padding(top=4, bottom=4, left=10, right=10),
                background=f'{pending_color}15',
                border_radius=20,
            )
            with me.box(style=status_style):
                me.text('분석 중...', style=me.Style(
                    font_size=12,
                    color=pending_color,
                    font_weight='500',
                ))


def empty_dashboard():
    """Render empty state with integrated search - modern dark theme."""
    from .stock_input import on_stock_input_blur, on_stock_input_enter, on_analyze_button_click, on_chip_click, on_mock_button_click
    from state.state import AppState

    app_state = me.state(AppState)

    # Full page container
    container_style = me.Style(
        display='flex',
        flex_direction='column',
        align_items='center',
        justify_content='center',
        min_height='100vh',
        padding=me.Padding.all(40),
        background=COLORS['background'],
    )

    with me.box(style=container_style):
        # Logo/Icon
        icon_bg = me.Style(
            display='flex',
            align_items='center',
            justify_content='center',
            width=72,
            height=72,
            background=f'linear-gradient(135deg, {COLORS["accent"]}25 0%, {COLORS["accent"]}08 100%)',
            border_radius=18,
            margin=me.Margin(bottom=24),
        )
        with me.box(style=icon_bg):
            me.icon('trending_up', style=me.Style(
                font_size=36,
                color=COLORS['accent'],
            ))

        # Title
        me.text('AI 주식 분석', style=me.Style(
            font_size=28,
            color=COLORS['text_primary'],
            font_weight='700',
            margin=me.Margin(bottom=8),
        ))

        # Subtitle
        me.text('종목을 검색하여 AI 기반 종합 분석을 받아보세요', style=me.Style(
            font_size=15,
            color=COLORS['text_secondary'],
            margin=me.Margin(bottom=32),
        ))

        # Search input container - main focus
        search_container = me.Style(
            display='flex',
            flex_direction='row',
            align_items='center',
            gap=12,
            width='100%',
            max_width=560,
            margin=me.Margin(bottom=24),
        )

        with me.box(style=search_container):
            # Input wrapper
            input_wrapper = me.Style(
                display='flex',
                flex_direction='row',
                align_items='center',
                gap=12,
                flex_grow=1,
                padding=me.Padding(top=4, bottom=4, left=16, right=8),
                background=COLORS['card_background'],
                border=me.Border.all(me.BorderSide(width=1, color=COLORS['card_border'], style='solid')),
                border_radius=12,
            )
            with me.box(style=input_wrapper):
                me.icon('search', style=me.Style(
                    color=COLORS['text_secondary'],
                    font_size=22,
                ))
                # Native input with custom styling
                me.native_textarea(
                    value=app_state.stock_input_value,
                    on_blur=on_stock_input_blur,
                    autosize=True,
                    min_rows=1,
                    max_rows=1,
                    style=me.Style(
                        flex_grow=1,
                        background='transparent',
                        color=COLORS['text_primary'],
                        font_size=16,
                        border=me.Border.all(me.BorderSide(width=0)),
                        outline='none',
                        padding=me.Padding(top=12, bottom=12, left=8, right=8),
                    ),
                    placeholder='종목명 또는 티커 입력 (예: AAPL, 삼성전자)',
                )

            # Analyze button
            btn_style = me.Style(
                display='flex',
                align_items='center',
                justify_content='center',
                padding=me.Padding(top=14, bottom=14, left=28, right=28),
                background=COLORS['accent'],
                border_radius=12,
                cursor='pointer',
            )
            with me.box(style=btn_style, on_click=on_analyze_button_click):
                me.text('분석하기', style=me.Style(
                    color='#FFFFFF',
                    font_size=15,
                    font_weight='600',
                ))

        # Mock button for testing
        mock_btn_style = me.Style(
            display='flex',
            align_items='center',
            gap=6,
            padding=me.Padding(top=10, bottom=10, left=16, right=16),
            background=COLORS['card_background'],
            border=me.Border.all(me.BorderSide(width=1, color=COLORS['hold'], style='solid')),
            border_radius=8,
            cursor='pointer',
            margin=me.Margin(bottom=24),
        )
        with me.box(style=mock_btn_style, on_click=on_mock_button_click):
            me.icon('science', style=me.Style(
                color=COLORS['hold'],
                font_size=18,
            ))
            me.text('Mock 데이터 (CRWV)', style=me.Style(
                color=COLORS['hold'],
                font_size=13,
                font_weight='500',
            ))

        # Example tickers
        me.text('예시', style=me.Style(
            font_size=13,
            color=COLORS['text_secondary'],
            margin=me.Margin(bottom=12),
        ))

        # Example chips
        examples_container = me.Style(
            display='flex',
            flex_direction='row',
            gap=10,
            flex_wrap='wrap',
            justify_content='center',
        )

        example_tickers = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL']

        with me.box(style=examples_container):
            for ticker in example_tickers:
                chip_style = me.Style(
                    padding=me.Padding(top=8, bottom=8, left=16, right=16),
                    background=COLORS['card_background'],
                    border=me.Border.all(me.BorderSide(width=1, color=COLORS['card_border'], style='solid')),
                    border_radius=20,
                    cursor='pointer',
                )
                with me.box(key=ticker, style=chip_style, on_click=on_chip_click):
                    me.text(ticker, style=me.Style(
                        color=COLORS['text_secondary'],
                        font_size=14,
                    ))

        # Recent searches (if any)
        if app_state.recent_searches:
            me.text('최근 검색', style=me.Style(
                font_size=13,
                color=COLORS['text_secondary'],
                margin=me.Margin(top=32, bottom=12),
            ))

            recent_container = me.Style(
                display='flex',
                flex_direction='row',
                gap=10,
                flex_wrap='wrap',
                justify_content='center',
            )

            with me.box(style=recent_container):
                for ticker in app_state.recent_searches[:5]:
                    chip_style = me.Style(
                        padding=me.Padding(top=8, bottom=8, left=16, right=16),
                        background=f'{COLORS["accent"]}15',
                        border=me.Border.all(me.BorderSide(width=1, color=f'{COLORS["accent"]}30', style='solid')),
                        border_radius=20,
                        cursor='pointer',
                    )
                    with me.box(key=ticker, style=chip_style, on_click=on_chip_click):
                        me.text(ticker, style=me.Style(
                            color=COLORS['accent'],
                            font_size=14,
                        ))


def error_dashboard(error_message: str):
    """Render error state."""
    container_style = me.Style(
        display='flex',
        flex_direction='column',
        align_items='center',
        justify_content='center',
        min_height=400,
        gap=20,
        padding=me.Padding.all(40),
    )

    with me.box(style=container_style):
        # Icon container with gradient background
        icon_bg = me.Style(
            display='flex',
            align_items='center',
            justify_content='center',
            width=80,
            height=80,
            background=f'linear-gradient(135deg, {COLORS["bearish"]}30 0%, {COLORS["bearish"]}10 100%)',
            border_radius=20,
            margin=me.Margin(bottom=8),
        )
        with me.box(style=icon_bg):
            me.icon('error_outline', style=me.Style(
                font_size=40,
                color=COLORS['bearish'],
            ))

        me.text('분석 실패', style=me.Style(
            font_size=18,
            color=COLORS['text_primary'],
            font_weight='bold',
        ))
        me.text(error_message, style=me.Style(
            font_size=14,
            color=COLORS['text_secondary'],
            text_align='center',
            max_width=400,
        ))