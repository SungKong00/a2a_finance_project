"""
Analysis Card Component

Displays individual analysis results (technical, fundamental, sentiment, risk)
in a card format with expandable details.
"""

import mesop as me
from typing import Optional, Dict, Any

from styles.stock_styles import (
    COLORS,
    CARD_STYLE,
    CARD_HEADER_STYLE,
    CARD_TITLE_STYLE,
    CARD_BODY_STYLE,
    CARD_METRIC_ROW_STYLE,
    CARD_METRIC_LABEL_STYLE,
    CARD_METRIC_VALUE_STYLE,
    CARD_EXPAND_BUTTON_STYLE,
    CARD_DETAIL_STYLE,
    CARD_CONFIG,
    get_badge_color,
    badge_style,
    BADGE_VALUE_STYLE,
)


def analysis_card(
    card_type: str,
    data: Dict[str, Any],
    expanded: bool = False,
    on_expand_click: Optional[callable] = None,
):
    """
    Render an analysis card component.

    Args:
        card_type: One of 'technical', 'fundamental', 'sentiment', 'risk'
        data: Dictionary containing analysis data
        expanded: Whether the card details are expanded
        on_expand_click: Callback for expand button click
    """
    config = CARD_CONFIG.get(card_type, {})
    title = config.get('title', card_type.title())
    icon = config.get('icon', 'info')
    color = config.get('color', COLORS['neutral'])

    # Dark theme card style
    dark_card_style = me.Style(
        background=COLORS['card_background'],
        border_radius=12,
        padding=me.Padding.all(16),
        box_shadow=f'0 4px 12px {COLORS["card_shadow"]}',
        border=me.Border.all(
            me.BorderSide(width=1, color=COLORS['card_border'], style='solid')
        ),
    )

    with me.box(style=dark_card_style):
        # Header
        _render_card_header(title, icon, color, data)

        # Body with metrics
        _render_card_body(card_type, data)

        # Expandable details
        if data.get('summary') or data.get('analysis'):
            _render_expand_section(data, expanded, on_expand_click)


def _render_card_header(title: str, icon: str, color: str, data: Dict[str, Any]):
    """Render card header with title and status badge."""
    header_style = me.Style(
        display='flex',
        flex_direction='row',
        align_items='center',
        justify_content='space-between',
        padding=me.Padding(bottom=12),
        border=me.Border(
            bottom=me.BorderSide(width=1, color=COLORS['divider'], style='solid')
        ),
    )

    with me.box(style=header_style):
        # Title with icon
        title_container = me.Style(
            display='flex',
            align_items='center',
            gap=8,
        )
        with me.box(style=title_container):
            me.icon(icon, style=me.Style(color=color, font_size=20))
            me.text(title, style=me.Style(
                font_size=16,
                font_weight='bold',
                color=COLORS['text_primary'],
            ))

        # Status badge (trend, sentiment, risk level, etc.)
        status = _get_status_value(data)
        if status:
            badge_color = get_badge_color(status)
            with me.box(style=badge_style(badge_color)):
                me.text(status.upper(), style=me.Style(
                    font_size=12,
                    font_weight='bold',
                    color=badge_color,
                ))


def _get_status_value(data: Dict[str, Any]) -> Optional[str]:
    """Extract the main status value from data."""
    # Check keys in order of priority for each card type
    for key in ['trend', 'sentiment_verdict', 'risk_level', 'valuation_verdict', 'recommendation']:
        if key in data and data[key]:
            return str(data[key])
    return None


def _render_card_body(card_type: str, data: Dict[str, Any]):
    """Render card body with relevant metrics."""
    body_style = me.Style(
        padding=me.Padding(top=12),
    )

    with me.box(style=body_style):
        if card_type == 'technical':
            _render_technical_metrics(data)
        elif card_type == 'fundamental':
            _render_fundamental_metrics(data)
        elif card_type == 'sentiment':
            _render_sentiment_metrics(data)
        elif card_type == 'risk':
            _render_risk_metrics(data)


def _render_metric_row(label: str, value: Any, color: Optional[str] = None):
    """Render a single metric row."""
    row_style = me.Style(
        display='flex',
        flex_direction='row',
        justify_content='center',
        gap=24,
        padding=me.Padding(top=6, bottom=6),
    )

    with me.box(style=row_style):
        me.text(f"{label}:", style=me.Style(
            font_size=14,
            color=COLORS['text_secondary'],
            min_width=120,
            text_align='right',
        ))
        me.text(str(value), style=me.Style(
            font_size=14,
            font_weight='500',
            color=color or COLORS['text_primary'],
            min_width=120,
        ))


def _render_summary(data: Dict[str, Any]):
    """Render summary/review section with markdown support."""
    summary = data.get('summary') or data.get('analysis_content') or data.get('analysis')
    if summary:
        summary_style = me.Style(
            margin=me.Margin(top=12),
            padding=me.Padding.all(12),
            background=COLORS['surface'],
            border_radius=8,
            font_size=13,
            line_height='1.6',
            color=COLORS['text_secondary'],
        )
        with me.box(style=summary_style):
            me.markdown(summary)


def _render_technical_metrics(data: Dict[str, Any]):
    """Render technical analysis metrics."""
    # Format support/resistance levels
    support = data.get('support_levels', [])
    resistance = data.get('resistance_levels', [])
    support_str = ', '.join(f'${v:,.0f}' for v in support[:2]) if support else 'N/A'
    resistance_str = ', '.join(f'${v:,.0f}' for v in resistance[:2]) if resistance else 'N/A'

    # Format current price
    current_price = data.get('current_price')
    price_str = f'${current_price:,.2f}' if current_price else 'N/A'

    metrics = [
        ('Trend', data.get('trend', 'N/A')),
        ('Current Price', price_str),
        ('RSI', data.get('rsi', 'N/A')),
        ('MACD Signal', data.get('macd_signal', 'N/A')),
        ('Support', support_str),
        ('Resistance', resistance_str),
    ]

    for label, value in metrics:
        if value and value != 'N/A':
            color = None
            if label == 'Trend':
                color = get_badge_color(str(value))
            _render_metric_row(label, value, color)

    # Render summary
    _render_summary(data)


def _render_fundamental_metrics(data: Dict[str, Any]):
    """Render fundamental analysis metrics."""
    # Format market cap
    market_cap = data.get('market_cap')
    if market_cap:
        if market_cap >= 1e12:
            cap_str = f'${market_cap/1e12:.2f}T'
        elif market_cap >= 1e9:
            cap_str = f'${market_cap/1e9:.2f}B'
        else:
            cap_str = f'${market_cap/1e6:.2f}M'
    else:
        cap_str = 'N/A'

    # Format percentages
    roe = data.get('roe')
    roe_str = f'{roe:.1f}%' if roe is not None else 'N/A'

    revenue_growth = data.get('revenue_growth')
    growth_str = f'{revenue_growth:.1f}%' if revenue_growth is not None else 'N/A'

    metrics = [
        ('Market Cap', cap_str),
        ('P/E Ratio', data.get('pe_ratio', 'N/A')),
        ('P/B Ratio', data.get('pb_ratio', 'N/A')),
        ('ROE', roe_str),
        ('Revenue Growth', growth_str),
        ('Valuation', data.get('valuation_verdict', 'N/A')),
    ]

    for label, value in metrics:
        if value and value != 'N/A':
            color = None
            if label == 'Valuation':
                color = get_badge_color(str(value))
            _render_metric_row(label, value, color)

    # Render summary
    _render_summary(data)


def _render_sentiment_metrics(data: Dict[str, Any]):
    """Render sentiment analysis metrics."""
    # Format sentiment score
    score = data.get('sentiment_score')
    if score is not None:
        # Handle both 0-1 and -1 to 1 scales
        if -1 <= score <= 1:
            score_str = f'{score:.2f}'
        else:
            score_str = f'{score:.1f}'
    else:
        score_str = 'N/A'

    metrics = [
        ('Sentiment', data.get('sentiment_verdict', 'N/A')),
        ('Score', score_str),
        ('Analyst Consensus', data.get('analyst_consensus', 'N/A')),
    ]

    for label, value in metrics:
        if value and value != 'N/A':
            color = None
            if label in ('Sentiment', 'Analyst Consensus'):
                color = get_badge_color(str(value))
            _render_metric_row(label, value, color)

    # Render top headlines if available
    headlines = data.get('top_headlines', [])
    if headlines:
        me.text('Top Headlines:', style=me.Style(
            font_size=13,
            color=COLORS['text_secondary'],
            margin=me.Margin(top=12, bottom=8),
        ))
        for headline in headlines[:3]:
            me.text(f'• {headline}', style=me.Style(
                font_size=12,
                color=COLORS['text_secondary'],
                line_height='1.5',
            ))

    # Render summary
    _render_summary(data)


def _render_risk_metrics(data: Dict[str, Any]):
    """Render risk assessment metrics."""
    # Format volatility and max drawdown as percentages
    volatility = data.get('volatility')
    vol_str = f'{volatility:.1f}%' if volatility is not None else 'N/A'

    max_dd = data.get('max_drawdown')
    dd_str = f'{max_dd:.1f}%' if max_dd is not None else 'N/A'

    # Format beta and sharpe ratio
    beta = data.get('beta')
    beta_str = f'{beta:.2f}' if beta is not None else 'N/A'

    sharpe = data.get('sharpe_ratio')
    sharpe_str = f'{sharpe:.2f}' if sharpe is not None else 'N/A'

    metrics = [
        ('Risk Level', data.get('risk_level', 'N/A')),
        ('Beta', beta_str),
        ('Volatility', vol_str),
        ('Sharpe Ratio', sharpe_str),
        ('Max Drawdown', dd_str),
    ]

    for label, value in metrics:
        if value and value != 'N/A':
            color = None
            if label == 'Risk Level':
                color = get_badge_color(str(value))
            _render_metric_row(label, value, color)

    # Render summary
    _render_summary(data)


def _render_expand_section(
    data: Dict[str, Any],
    expanded: bool,
    on_expand_click: Optional[callable],
):
    """Render expandable details section."""
    # Expand button
    expand_style = me.Style(
        cursor='pointer',
        padding=me.Padding(top=12),
        font_size=13,
        color=COLORS['accent'],
        display='flex',
        align_items='center',
        gap=4,
    )

    with me.box(style=expand_style, on_click=on_expand_click):
        icon_name = 'expand_less' if expanded else 'expand_more'
        me.icon(icon_name, style=me.Style(font_size=18))
        me.text('Hide Details' if expanded else 'Show Details')

    # Expanded content
    if expanded:
        detail_style = me.Style(
            padding=me.Padding(top=12),
            font_size=14,
            line_height='1.6',
            color=COLORS['text_secondary'],
            border=me.Border(
                top=me.BorderSide(width=1, color=COLORS['divider'], style='solid')
            ),
            margin=me.Margin(top=8),
        )

        with me.box(style=detail_style):
            # Use analysis_content from schema, fallback to other fields
            summary = (
                data.get('analysis_content') or
                data.get('summary') or
                data.get('analysis') or
                ''
            )
            me.text(summary)
