"""
Stock Analysis UI Styles

Color palette, card styles, badge styles, and gauge styles for
the stock analysis dashboard.
"""

import mesop as me


# =============================================================================
# COLOR PALETTE
# =============================================================================

COLORS = {
    # Trend/Sentiment
    'bullish': '#4CAF50',       # Green - upward
    'bearish': '#F44336',       # Red - downward
    'neutral': '#9E9E9E',       # Gray - neutral

    # Trading Recommendations
    'strong_buy': '#1B5E20',    # Dark green
    'buy': '#2196F3',           # Blue
    'hold': '#FF9800',          # Orange
    'sell': '#FF5722',          # Orange-red
    'strong_sell': '#B71C1C',   # Dark red

    # Risk Levels
    'low_risk': '#8BC34A',      # Light green
    'moderate_risk': '#FFC107', # Yellow
    'high_risk': '#FF5722',     # Orange
    'very_high_risk': '#E91E63', # Pink

    # Valuation
    'undervalued': '#4CAF50',   # Green
    'fairly_valued': '#2196F3', # Blue
    'overvalued': '#F44336',    # Red

    # UI Base
    'card_border': '#E0E0E0',
    'card_shadow': 'rgba(0,0,0,0.1)',
    'text_primary': '#212121',
    'text_secondary': '#757575',
    'divider': '#EEEEEE',
}


# =============================================================================
# BADGE COLOR MAPPING
# =============================================================================

def get_badge_color(value: str) -> str:
    """Get appropriate color for a badge value."""
    value_lower = value.lower() if value else ''

    # Trend/Sentiment
    if value_lower in ('bullish', 'positive'):
        return COLORS['bullish']
    if value_lower in ('bearish', 'negative'):
        return COLORS['bearish']
    if value_lower in ('neutral',):
        return COLORS['neutral']

    # Recommendations
    if value_lower in ('strong buy', 'strong_buy', 'strongbuy'):
        return COLORS['strong_buy']
    if value_lower in ('buy',):
        return COLORS['buy']
    if value_lower in ('hold',):
        return COLORS['hold']
    if value_lower in ('sell',):
        return COLORS['sell']
    if value_lower in ('strong sell', 'strong_sell', 'strongsell'):
        return COLORS['strong_sell']

    # Risk
    if value_lower in ('low', 'low risk'):
        return COLORS['low_risk']
    if value_lower in ('moderate', 'moderate risk', 'medium'):
        return COLORS['moderate_risk']
    if value_lower in ('high', 'high risk'):
        return COLORS['high_risk']
    if value_lower in ('very high', 'very_high', 'veryhigh', 'very high risk'):
        return COLORS['very_high_risk']

    # Valuation
    if value_lower in ('undervalued',):
        return COLORS['undervalued']
    if value_lower in ('fairly valued', 'fairly_valued', 'fairlyvalued', 'fair'):
        return COLORS['fairly_valued']
    if value_lower in ('overvalued',):
        return COLORS['overvalued']

    return COLORS['neutral']


# =============================================================================
# INPUT STYLES
# =============================================================================

STOCK_INPUT_CONTAINER_STYLE = me.Style(
    display='flex',
    flex_direction='column',
    gap=12,
    padding=me.Padding.all(16),
    background=me.theme_var('surface'),
    border_radius=12,
    margin=me.Margin(bottom=16),
)

STOCK_INPUT_ROW_STYLE = me.Style(
    display='flex',
    flex_direction='row',
    gap=12,
    align_items='center',
)

STOCK_INPUT_FIELD_STYLE = me.Style(
    flex_grow=1,
)

STOCK_INPUT_BUTTON_STYLE = me.Style(
    flex_shrink=0,
)

RECENT_SEARCHES_STYLE = me.Style(
    display='flex',
    flex_direction='row',
    gap=8,
    flex_wrap='wrap',
    margin=me.Margin(top=8),
)

SEARCH_CHIP_STYLE = me.Style(
    padding=me.Padding(top=4, bottom=4, left=12, right=12),
    background='#E3F2FD',
    border_radius=16,
    font_size=14,
    cursor='pointer',
)

SEARCH_CHIP_HOVER_STYLE = me.Style(
    padding=me.Padding(top=4, bottom=4, left=12, right=12),
    background='#BBDEFB',
    border_radius=16,
    font_size=14,
    cursor='pointer',
)

HINT_TEXT_STYLE = me.Style(
    font_size=13,
    color=COLORS['text_secondary'],
)


# =============================================================================
# DASHBOARD STYLES
# =============================================================================

DASHBOARD_CONTAINER_STYLE = me.Style(
    display='flex',
    flex_direction='column',
    gap=16,
    padding=me.Padding.all(16),
)

DASHBOARD_HEADER_STYLE = me.Style(
    display='flex',
    flex_direction='row',
    align_items='center',
    gap=12,
    padding=me.Padding(bottom=16),
    border=me.Border(
        bottom=me.BorderSide(width=1, color=COLORS['divider'], style='solid')
    ),
)

DASHBOARD_TITLE_STYLE = me.Style(
    font_size=24,
    font_weight='bold',
    color=COLORS['text_primary'],
)


# =============================================================================
# SUMMARY BADGE STYLES
# =============================================================================

SUMMARY_ROW_STYLE = me.Style(
    display='flex',
    flex_direction='row',
    gap=12,
    flex_wrap='wrap',
    margin=me.Margin(bottom=16),
    justify_content='center',
)


def badge_style(color: str) -> me.Style:
    """Create badge style with given color."""
    return me.Style(
        display='flex',
        flex_direction='column',
        align_items='center',
        justify_content='center',
        padding=me.Padding(top=12, bottom=12, left=16, right=16),
        background=color + '20',  # 20% opacity
        border=me.Border.all(me.BorderSide(width=2, color=color, style='solid')),
        border_radius=12,
        min_width=100,
    )


BADGE_ICON_STYLE = me.Style(
    font_size=24,
    margin=me.Margin(bottom=4),
)

BADGE_VALUE_STYLE = me.Style(
    font_size=14,
    font_weight='bold',
)

BADGE_LABEL_STYLE = me.Style(
    font_size=11,
    color=COLORS['text_secondary'],
)


# =============================================================================
# CARD STYLES
# =============================================================================

CARD_STYLE = me.Style(
    background=me.theme_var('surface'),
    border_radius=12,
    padding=me.Padding.all(16),
    box_shadow=f'0 2px 8px {COLORS["card_shadow"]}',
    border=me.Border.all(
        me.BorderSide(width=1, color=COLORS['card_border'], style='solid')
    ),
)

CARD_HEADER_STYLE = me.Style(
    display='flex',
    flex_direction='row',
    align_items='center',
    justify_content='space-between',
    padding=me.Padding(bottom=12),
    border=me.Border(
        bottom=me.BorderSide(width=1, color=COLORS['divider'], style='solid')
    ),
)

CARD_TITLE_STYLE = me.Style(
    font_size=16,
    font_weight='bold',
    display='flex',
    align_items='center',
    gap=8,
)

CARD_BODY_STYLE = me.Style(
    padding=me.Padding(top=12),
)

CARD_METRIC_ROW_STYLE = me.Style(
    display='flex',
    flex_direction='row',
    justify_content='space-between',
    padding=me.Padding(top=4, bottom=4),
)

CARD_METRIC_LABEL_STYLE = me.Style(
    font_size=14,
    color=COLORS['text_secondary'],
)

CARD_METRIC_VALUE_STYLE = me.Style(
    font_size=14,
    font_weight='500',
)

CARD_EXPAND_BUTTON_STYLE = me.Style(
    cursor='pointer',
    padding=me.Padding(top=8),
    font_size=13,
    color=COLORS['buy'],
)

CARD_DETAIL_STYLE = me.Style(
    padding=me.Padding(top=12),
    font_size=14,
    line_height='1.6',
)


# =============================================================================
# GRID STYLES
# =============================================================================

GRID_2X2_STYLE = me.Style(
    display='grid',
    grid_template_columns='1fr 1fr',
    gap=16,
)

GRID_1X1_STYLE = me.Style(
    display='flex',
    flex_direction='column',
    gap=16,
)


# =============================================================================
# GAUGE STYLES
# =============================================================================

GAUGE_CONTAINER_STYLE = me.Style(
    display='flex',
    flex_direction='column',
    gap=4,
    margin=me.Margin(top=4, bottom=4),
)

GAUGE_LABEL_ROW_STYLE = me.Style(
    display='flex',
    flex_direction='row',
    justify_content='space-between',
    font_size=13,
)

GAUGE_TRACK_STYLE = me.Style(
    height=8,
    background='#E0E0E0',
    border_radius=4,
    overflow='hidden',
)


def gauge_fill_style(percentage: float, color: str) -> me.Style:
    """Create gauge fill style with given percentage and color."""
    return me.Style(
        height=8,
        width=f'{min(100, max(0, percentage))}%',
        background=color,
        border_radius=4,
    )


# =============================================================================
# CARD TYPE CONFIGURATIONS
# =============================================================================

CARD_CONFIG = {
    'technical': {
        'title': 'Technical Analysis',
        'title_kr': '기술적 분석',
        'icon': 'show_chart',
        'color': '#2196F3',
    },
    'fundamental': {
        'title': 'Fundamental Analysis',
        'title_kr': '펀더멘털 분석',
        'icon': 'assessment',
        'color': '#4CAF50',
    },
    'sentiment': {
        'title': 'Market Sentiment',
        'title_kr': '시장 심리',
        'icon': 'mood',
        'color': '#FF9800',
    },
    'risk': {
        'title': 'Risk Assessment',
        'title_kr': '리스크 평가',
        'icon': 'warning',
        'color': '#F44336',
    },
}


# =============================================================================
# METRIC CONFIGURATIONS
# =============================================================================

METRIC_CONFIG = {
    'rsi': {
        'label': 'RSI',
        'min': 0,
        'max': 100,
        'good_range': (30, 70),  # Neutral zone
    },
    'beta': {
        'label': 'Beta',
        'min': 0,
        'max': 2,
        'good_range': (0.8, 1.2),
    },
    'pe_ratio': {
        'label': 'P/E Ratio',
        'min': 0,
        'max': 50,
        'good_range': (10, 25),
    },
    'roe': {
        'label': 'ROE',
        'min': 0,
        'max': 100,
        'good_range': (15, 50),
    },
    'volatility': {
        'label': 'Volatility',
        'min': 0,
        'max': 100,
        'good_range': (10, 30),
    },
    'sharpe_ratio': {
        'label': 'Sharpe Ratio',
        'min': -1,
        'max': 3,
        'good_range': (1, 2),
    },
    'sentiment_score': {
        'label': 'Sentiment Score',
        'min': 0,
        'max': 10,
        'good_range': (5, 8),
    },
}


def get_metric_color(metric_name: str, value: float) -> str:
    """Get color for metric value based on good range."""
    config = METRIC_CONFIG.get(metric_name)
    if not config:
        return COLORS['neutral']

    good_min, good_max = config.get('good_range', (0, 100))

    if good_min <= value <= good_max:
        return COLORS['bullish']
    elif value < good_min:
        return COLORS['bearish'] if metric_name != 'pe_ratio' else COLORS['bullish']
    else:
        return COLORS['bearish'] if metric_name != 'pe_ratio' else COLORS['bearish']
