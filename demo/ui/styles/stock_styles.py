"""
Stock Analysis UI Styles

Color palette, card styles, badge styles, and gauge styles for
the stock analysis dashboard.
"""

import mesop as me


# =============================================================================
# COLOR PALETTE - DARK THEME
# =============================================================================

COLORS = {
    # Trend/Sentiment
    'bullish': '#66BB6A',       # Green - upward (brighter for dark)
    'bearish': '#EF5350',       # Red - downward
    'neutral': '#BDBDBD',       # Gray - neutral

    # Trading Recommendations
    'strong_buy': '#4CAF50',    # Green (brighter for dark)
    'buy': '#42A5F5',           # Blue
    'hold': '#FFA726',          # Orange
    'sell': '#FF7043',          # Orange-red
    'strong_sell': '#E53935',   # Red

    # Risk Levels
    'low_risk': '#9CCC65',      # Light green
    'moderate_risk': '#FFCA28', # Yellow
    'high_risk': '#FF7043',     # Orange
    'very_high_risk': '#EC407A', # Pink

    # Valuation
    'undervalued': '#66BB6A',   # Green
    'fairly_valued': '#42A5F5', # Blue
    'overvalued': '#EF5350',    # Red

    # UI Base - Dark Theme
    'background': '#121212',
    'surface': '#1E1E1E',
    'card_background': '#252525',
    'card_border': '#333333',
    'card_shadow': 'rgba(0,0,0,0.4)',
    'text_primary': '#E0E0E0',
    'text_secondary': '#9E9E9E',
    'divider': '#333333',
    'accent': '#BB86FC',
}


# =============================================================================
# BADGE COLOR MAPPING
# =============================================================================

def get_badge_color(value: str) -> str:
    """Get appropriate color for a badge value."""
    value_lower = value.lower() if value else ''

    # Trend/Sentiment (English + Korean)
    if value_lower in ('bullish', 'positive', '강세', '긍정', '긍정적'):
        return COLORS['bullish']
    if value_lower in ('bearish', 'negative', '약세', '부정', '부정적'):
        return COLORS['bearish']
    if value_lower in ('neutral', '중립', '보합'):
        return COLORS['neutral']

    # Recommendations (English + Korean)
    if value_lower in ('strong buy', 'strong_buy', 'strongbuy', '적극 매수', '적극매수'):
        return COLORS['strong_buy']
    if value_lower in ('buy', '매수'):
        return COLORS['buy']
    if value_lower in ('hold', '보유', '중립'):
        return COLORS['hold']
    if value_lower in ('sell', '매도'):
        return COLORS['sell']
    if value_lower in ('strong sell', 'strong_sell', 'strongsell', '적극 매도', '적극매도'):
        return COLORS['strong_sell']

    # Risk (English + Korean)
    if value_lower in ('low', 'low risk', '낮음', '저위험'):
        return COLORS['low_risk']
    if value_lower in ('moderate', 'moderate risk', 'medium', '보통', '중간'):
        return COLORS['moderate_risk']
    if value_lower in ('high', 'high risk', '높음', '고위험'):
        return COLORS['high_risk']
    if value_lower in ('very high', 'very_high', 'veryhigh', 'very high risk', '매우 높음', '매우높음', '초고위험'):
        return COLORS['very_high_risk']

    # Valuation (English + Korean)
    if value_lower in ('undervalued', '저평가'):
        return COLORS['undervalued']
    if value_lower in ('fairly valued', 'fairly_valued', 'fairlyvalued', 'fair', '적정가', '적정'):
        return COLORS['fairly_valued']
    if value_lower in ('overvalued', '고평가'):
        return COLORS['overvalued']

    return COLORS['neutral']


# =============================================================================
# INPUT STYLES
# =============================================================================

STOCK_INPUT_CONTAINER_STYLE = me.Style(
    display='flex',
    flex_direction='column',
    gap=12,
    padding=me.Padding.all(20),
    background=COLORS['surface'],
    border_radius=12,
    margin=me.Margin(bottom=16),
    border=me.Border.all(
        me.BorderSide(width=1, color=COLORS['card_border'], style='solid')
    ),
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
    background='#2D3748',
    border_radius=16,
    font_size=14,
    cursor='pointer',
    color=COLORS['text_primary'],
)

SEARCH_CHIP_HOVER_STYLE = me.Style(
    padding=me.Padding(top=4, bottom=4, left=12, right=12),
    background='#4A5568',
    border_radius=16,
    font_size=14,
    cursor='pointer',
    color=COLORS['text_primary'],
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
    background='#333333',
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
        'title': '기술적 분석',
        'icon': 'show_chart',
        'color': '#2196F3',
    },
    'fundamental': {
        'title': '펀더멘털 분석',
        'icon': 'assessment',
        'color': '#4CAF50',
    },
    'sentiment': {
        'title': '시장 심리',
        'icon': 'mood',
        'color': '#FF9800',
    },
    'risk': {
        'title': '리스크 평가',
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
