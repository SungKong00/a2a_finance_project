"""
Summary Badge Component

Displays key summary indicators as colored badges at the top of the dashboard.
Includes recommendation, trend, risk level, and valuation badges.
"""

import mesop as me
from typing import Optional

from styles.stock_styles import (
    COLORS,
    SUMMARY_ROW_STYLE,
    badge_style,
    BADGE_ICON_STYLE,
    BADGE_VALUE_STYLE,
    BADGE_LABEL_STYLE,
    get_badge_color,
)


# Icon mappings for different badge types
BADGE_ICONS = {
    # Recommendations
    'strong_buy': 'trending_up',
    'buy': 'arrow_upward',
    'hold': 'remove',
    'sell': 'arrow_downward',
    'strong_sell': 'trending_down',

    # Trends
    'bullish': 'trending_up',
    'bearish': 'trending_down',
    'neutral': 'trending_flat',

    # Sentiment
    'positive': 'sentiment_satisfied',
    'negative': 'sentiment_dissatisfied',

    # Risk levels
    'low': 'verified_user',
    'moderate': 'shield',
    'high': 'warning',
    'very_high': 'dangerous',

    # Valuation
    'undervalued': 'thumb_up',
    'fairly_valued': 'thumbs_up_down',
    'overvalued': 'thumb_down',
}


def get_badge_icon(value: str) -> str:
    """Get appropriate icon for a badge value."""
    value_lower = value.lower().replace(' ', '_') if value else ''
    return BADGE_ICONS.get(value_lower, 'info')


def summary_badge(
    label: str,
    value: str,
    icon: Optional[str] = None,
):
    """
    Render a single summary badge.

    Args:
        label: The badge label (e.g., "Recommendation", "Trend")
        value: The badge value (e.g., "Buy", "Bullish")
        icon: Optional custom icon (auto-detected if not provided)
    """
    color = get_badge_color(value)
    badge_icon = icon or get_badge_icon(value)

    # Dark theme badge style
    dark_badge_style = me.Style(
        display='flex',
        flex_direction='column',
        align_items='center',
        justify_content='center',
        padding=me.Padding(top=12, bottom=12, left=20, right=20),
        background=color + '15',  # 15% opacity for dark theme
        border=me.Border.all(me.BorderSide(width=2, color=color, style='solid')),
        border_radius=12,
        min_width=110,
    )

    with me.box(style=dark_badge_style):
        # Icon
        me.icon(badge_icon, style=me.Style(
            font_size=24,
            color=color,
            margin=me.Margin(bottom=4),
        ))

        # Value
        me.text(value.upper() if value else 'N/A', style=me.Style(
            font_size=14,
            font_weight='bold',
            color=color,
        ))

        # Label
        me.text(label, style=me.Style(
            font_size=11,
            color=COLORS['text_secondary'],
            margin=me.Margin(top=2),
        ))


def summary_badge_row(badges: list):
    """
    Render a row of summary badges.

    Args:
        badges: List of dicts with 'label', 'value', and optional 'icon'
    """
    row_style = me.Style(
        display='flex',
        flex_direction='row',
        gap=12,
        flex_wrap='wrap',
        margin=me.Margin(bottom=20),
        justify_content='center',
    )

    with me.box(style=row_style):
        for badge in badges:
            summary_badge(
                label=badge.get('label', ''),
                value=badge.get('value', ''),
                icon=badge.get('icon'),
            )


def price_badge(
    current_price: float,
    change: float,
    change_percent: float,
    currency: str = '$',
):
    """
    Special badge for displaying stock price with change.

    Args:
        current_price: Current stock price
        change: Price change (absolute)
        change_percent: Price change (percentage)
        currency: Currency symbol
    """
    is_positive = change >= 0
    color = COLORS['bullish'] if is_positive else COLORS['bearish']
    icon = 'arrow_upward' if is_positive else 'arrow_downward'
    sign = '+' if is_positive else ''

    price_badge_style = me.Style(
        display='flex',
        flex_direction='column',
        align_items='center',
        justify_content='center',
        padding=me.Padding(top=12, bottom=12, left=24, right=24),
        background=COLORS['card_background'],
        border=me.Border.all(
            me.BorderSide(width=2, color=COLORS['card_border'], style='solid')
        ),
        border_radius=12,
        min_width=140,
    )

    with me.box(style=price_badge_style):
        # Current price
        me.text(f'{currency}{current_price:,.2f}', style=me.Style(
            font_size=20,
            font_weight='bold',
            color=COLORS['text_primary'],
        ))

        # Change row
        change_row_style = me.Style(
            display='flex',
            align_items='center',
            gap=4,
            margin=me.Margin(top=4),
        )

        with me.box(style=change_row_style):
            me.icon(icon, style=me.Style(font_size=16, color=color))
            me.text(
                f'{sign}{change:,.2f} ({sign}{change_percent:.2f}%)',
                style=me.Style(font_size=13, color=color, font_weight='500'),
            )

        # Label
        me.text('Current Price', style=me.Style(
            font_size=11,
            color=COLORS['text_secondary'],
            margin=me.Margin(top=4),
        ))


def score_badge(
    label: str,
    score: float,
    max_score: float = 10,
    icon: str = 'stars',
):
    """
    Badge for displaying a numeric score.

    Args:
        label: Badge label
        score: Current score
        max_score: Maximum possible score
        icon: Icon to display
    """
    # Determine color based on score percentage
    percentage = (score / max_score) * 100 if max_score > 0 else 0

    if percentage >= 70:
        color = COLORS['bullish']
    elif percentage >= 40:
        color = COLORS['hold']
    else:
        color = COLORS['bearish']

    score_badge_style = me.Style(
        display='flex',
        flex_direction='column',
        align_items='center',
        justify_content='center',
        padding=me.Padding(top=12, bottom=12, left=20, right=20),
        background=color + '15',
        border=me.Border.all(me.BorderSide(width=2, color=color, style='solid')),
        border_radius=12,
        min_width=110,
    )

    with me.box(style=score_badge_style):
        me.icon(icon, style=me.Style(
            font_size=24,
            color=color,
            margin=me.Margin(bottom=4),
        ))

        me.text(f'{score:.1f}/{max_score:.0f}', style=me.Style(
            font_size=16,
            font_weight='bold',
            color=color,
        ))

        me.text(label, style=me.Style(
            font_size=11,
            color=COLORS['text_secondary'],
            margin=me.Margin(top=2),
        ))
