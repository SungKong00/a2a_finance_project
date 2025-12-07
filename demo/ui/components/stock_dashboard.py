"""
Stock Dashboard Component

Main dashboard layout that combines all analysis components
into a unified Perplexity-style dark theme interface.
"""

import mesop as me
from typing import Dict, Any, Optional

from styles.stock_styles import (
    COLORS,
    DASHBOARD_CONTAINER_STYLE,
    DASHBOARD_HEADER_STYLE,
    DASHBOARD_TITLE_STYLE,
    GRID_2X2_STYLE,
)
from .analysis_card import analysis_card
from .summary_badge import summary_badge_row, price_badge
from .metric_gauge import confidence_gauge


def stock_dashboard(
    ticker: str,
    analysis_data: Dict[str, Any],
    expanded_cards: Optional[Dict[str, bool]] = None,
):
    """
    Render the complete stock analysis dashboard.

    Args:
        ticker: Stock ticker symbol
        analysis_data: Dictionary containing all analysis results
        expanded_cards: Dictionary tracking which cards are expanded
    """
    if expanded_cards is None:
        expanded_cards = {}

    # Main dashboard container with dark theme
    dashboard_style = me.Style(
        display='flex',
        flex_direction='column',
        gap=16,
        padding=me.Padding.all(20),
        background=COLORS['background'],
        min_height='100vh',
    )

    with me.box(style=dashboard_style):
        # Header section
        _render_dashboard_header(ticker, analysis_data)

        # Summary badges row
        _render_summary_section(analysis_data)

        # Analysis cards grid
        _render_analysis_grid(analysis_data, expanded_cards)

        # Final recommendation section
        _render_recommendation_section(analysis_data)


def _render_dashboard_header(ticker: str, data: Dict[str, Any]):
    """Render dashboard header with ticker and price info."""
    header_style = me.Style(
        display='flex',
        flex_direction='row',
        align_items='center',
        justify_content='space-between',
        padding=me.Padding(bottom=16),
        border=me.Border(
            bottom=me.BorderSide(width=1, color=COLORS['divider'], style='solid')
        ),
    )

    with me.box(style=header_style):
        # Left side: ticker and name
        left_section = me.Style(
            display='flex',
            flex_direction='column',
            gap=4,
        )

        with me.box(style=left_section):
            me.text(ticker.upper(), style=me.Style(
                font_size=28,
                font_weight='bold',
                color=COLORS['text_primary'],
            ))

            company_name = data.get('company_name', '')
            if company_name:
                me.text(company_name, style=me.Style(
                    font_size=14,
                    color=COLORS['text_secondary'],
                ))

        # Right side: price badge (if available)
        price_data = data.get('price', {})
        if price_data:
            price_badge(
                current_price=price_data.get('current', 0),
                change=price_data.get('change', 0),
                change_percent=price_data.get('change_percent', 0),
            )


def _render_summary_section(data: Dict[str, Any]):
    """Render summary badges section."""
    badges = []

    # Extract key indicators from analysis data (using schema field names)
    if 'technical' in data and data['technical']:
        tech = data['technical']
        if tech.get('trend'):
            badges.append({'label': 'Trend', 'value': tech['trend']})

    if 'fundamental' in data and data['fundamental']:
        fund = data['fundamental']
        # Use valuation_verdict from schema
        valuation = fund.get('valuation_verdict') or fund.get('valuation')
        if valuation:
            badges.append({'label': 'Valuation', 'value': valuation})

    if 'sentiment' in data and data['sentiment']:
        sent = data['sentiment']
        # Use sentiment_verdict from schema
        sentiment = sent.get('sentiment_verdict') or sent.get('sentiment')
        if sentiment:
            badges.append({'label': 'Sentiment', 'value': sentiment})

    if 'risk' in data and data['risk']:
        risk = data['risk']
        if risk.get('risk_level'):
            badges.append({'label': 'Risk', 'value': risk['risk_level']})

    # Add recommendation if available
    recommendation = data.get('recommendation') or data.get('final_recommendation')
    if recommendation:
        badges.append({'label': 'Recommendation', 'value': recommendation})

    if badges:
        summary_badge_row(badges)


def _render_analysis_grid(data: Dict[str, Any], expanded_cards: Dict[str, bool]):
    """Render 2x2 grid of analysis cards."""
    grid_style = me.Style(
        display='grid',
        grid_template_columns='1fr 1fr',
        gap=16,
    )

    with me.box(style=grid_style):
        # 기술적 분석
        if 'technical' in data:
            analysis_card(
                card_type='technical',
                data=data['technical'],
                expanded=expanded_cards.get('technical', False),
            )

        # 펀더멘털 분석
        if 'fundamental' in data:
            analysis_card(
                card_type='fundamental',
                data=data['fundamental'],
                expanded=expanded_cards.get('fundamental', False),
            )

        # 시장 심리
        if 'sentiment' in data:
            analysis_card(
                card_type='sentiment',
                data=data['sentiment'],
                expanded=expanded_cards.get('sentiment', False),
            )

        # 리스크 평가
        if 'risk' in data:
            analysis_card(
                card_type='risk',
                data=data['risk'],
                expanded=expanded_cards.get('risk', False),
            )


def _render_recommendation_section(data: Dict[str, Any]):
    """Render final recommendation section."""
    recommendation = data.get('final_recommendation') or data.get('recommendation')
    summary = data.get('summary') or data.get('final_summary')
    confidence = data.get('confidence', 0)

    if not recommendation and not summary:
        return

    section_style = me.Style(
        background=COLORS['card_background'],
        border_radius=12,
        padding=me.Padding.all(20),
        margin=me.Margin(top=8),
        border=me.Border.all(
            me.BorderSide(width=1, color=COLORS['card_border'], style='solid')
        ),
    )

    with me.box(style=section_style):
        # Section header
        header_style = me.Style(
            display='flex',
            align_items='center',
            gap=8,
            margin=me.Margin(bottom=16),
        )

        with me.box(style=header_style):
            me.icon('summarize', style=me.Style(
                color=COLORS['accent'],
                font_size=24,
            ))
            me.text('Analysis Summary', style=me.Style(
                font_size=18,
                font_weight='bold',
                color=COLORS['text_primary'],
            ))

        # Recommendation badge
        if recommendation:
            from .summary_badge import summary_badge

            badge_container = me.Style(
                display='flex',
                justify_content='center',
                margin=me.Margin(bottom=16),
            )

            with me.box(style=badge_container):
                summary_badge(
                    label='Final Recommendation',
                    value=recommendation,
                )

        # Confidence gauge
        if confidence > 0:
            gauge_container = me.Style(
                max_width=200,
                margin=me.Margin(left='auto', right='auto', bottom=16),
            )

            with me.box(style=gauge_container):
                confidence_gauge(confidence, 'Analysis Confidence')

        # Summary text
        if summary:
            me.text(summary, style=me.Style(
                font_size=14,
                line_height='1.7',
                color=COLORS['text_secondary'],
            ))


def loading_dashboard(ticker: str = '', progress: dict = None):
    """Render loading state for the dashboard with progress indicators."""
    if progress is None:
        progress = {}

    container_style = me.Style(
        display='flex',
        flex_direction='column',
        align_items='center',
        justify_content='center',
        min_height=400,
        gap=24,
        padding=me.Padding.all(40),
        background=COLORS['background'],
    )

    with me.box(style=container_style):
        # Ticker display
        if ticker:
            me.text(ticker.upper(), style=me.Style(
                font_size=32,
                font_weight='bold',
                color=COLORS['text_primary'],
            ))

        # Spinner
        me.progress_spinner()

        me.text('분석 중...', style=me.Style(
            font_size=18,
            color=COLORS['text_secondary'],
        ))

        # Progress indicators for each agent
        agents = [
            ('technical', '기술적 분석', 'show_chart'),
            ('fundamental', '펀더멘털 분석', 'assessment'),
            ('sentiment', '시장 심리', 'mood'),
            ('risk', '리스크 평가', 'warning'),
        ]

        progress_container = me.Style(
            display='flex',
            flex_direction='column',
            gap=12,
            margin=me.Margin(top=16),
            width='100%',
            max_width=400,
        )

        with me.box(style=progress_container):
            for agent_key, agent_name, icon_name in agents:
                is_done = progress.get(agent_key, False)
                _render_progress_item(agent_name, icon_name, is_done)


def _render_progress_item(name: str, icon: str, is_done: bool):
    """Render a single progress item."""
    color = COLORS['bullish'] if is_done else COLORS['text_secondary']
    icon_name = 'check_circle' if is_done else icon

    row_style = me.Style(
        display='flex',
        align_items='center',
        gap=12,
        padding=me.Padding(top=8, bottom=8, left=16, right=16),
        background=COLORS['card_background'],
        border_radius=8,
        border=me.Border.all(
            me.BorderSide(width=1, color=COLORS['card_border'], style='solid')
        ),
    )

    with me.box(style=row_style):
        me.icon(icon_name, style=me.Style(
            font_size=20,
            color=color,
        ))
        me.text(name, style=me.Style(
            font_size=14,
            color=color,
            flex_grow=1,
        ))
        if is_done:
            me.text('완료', style=me.Style(
                font_size=12,
                color=COLORS['bullish'],
                font_weight='bold',
            ))
        else:
            me.text('대기 중...', style=me.Style(
                font_size=12,
                color=COLORS['text_secondary'],
            ))


def empty_dashboard():
    """Render empty state when no stock is selected."""
    container_style = me.Style(
        display='flex',
        flex_direction='column',
        align_items='center',
        justify_content='center',
        min_height=400,
        gap=16,
        padding=me.Padding.all(40),
    )

    with me.box(style=container_style):
        me.icon('search', style=me.Style(
            font_size=48,
            color=COLORS['text_secondary'],
        ))
        me.text('Enter a stock ticker to begin analysis', style=me.Style(
            font_size=18,
            color=COLORS['text_secondary'],
        ))
        me.text('Try searching for AAPL, GOOGL, MSFT, etc.', style=me.Style(
            font_size=14,
            color=COLORS['text_secondary'],
        ))


def error_dashboard(error_message: str):
    """Render error state."""
    container_style = me.Style(
        display='flex',
        flex_direction='column',
        align_items='center',
        justify_content='center',
        min_height=400,
        gap=16,
        padding=me.Padding.all(40),
    )

    with me.box(style=container_style):
        me.icon('error_outline', style=me.Style(
            font_size=48,
            color=COLORS['bearish'],
        ))
        me.text('Analysis Failed', style=me.Style(
            font_size=18,
            color=COLORS['text_primary'],
            font_weight='bold',
        ))
        me.text(error_message, style=me.Style(
            font_size=14,
            color=COLORS['text_secondary'],
            text_align='center',
        ))
