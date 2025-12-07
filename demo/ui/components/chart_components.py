"""
Chart Components for Stock Analysis Dashboard

Provides interactive chart visualizations using Plotly for:
- RSI Gauge (Technical Analysis)
- Support/Resistance Levels (Technical Analysis)
- Valuation Comparison Bar Chart (Fundamental Analysis)
- Risk Level Gauge (Risk Assessment)
- Sentiment Gauge (Sentiment Analysis)
"""

import mesop as me
import plotly.graph_objects as go
from typing import Optional, List, Dict, Any

from styles.stock_styles import COLORS


# =============================================================================
# CHART THEME CONFIGURATION
# =============================================================================

CHART_THEME = {
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font_color': COLORS['text_primary'],
    'font_family': 'Inter, sans-serif',
}


def _hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Convert hex color to rgba format for Plotly compatibility."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    elif len(hex_color) == 3:
        r, g, b = int(hex_color[0]*2, 16), int(hex_color[1]*2, 16), int(hex_color[2]*2, 16)
    else:
        return f'rgba(128,128,128,{alpha})'
    return f'rgba({r},{g},{b},{alpha})'


def _get_chart_layout(height: int = 200, margin: Optional[Dict] = None) -> Dict:
    """Get common chart layout configuration."""
    default_margin = dict(l=20, r=20, t=30, b=20)
    return {
        'paper_bgcolor': CHART_THEME['paper_bgcolor'],
        'plot_bgcolor': CHART_THEME['plot_bgcolor'],
        'font': {
            'color': CHART_THEME['font_color'],
            'family': CHART_THEME['font_family'],
            'size': 12,
        },
        'height': height,
        'margin': margin or default_margin,
    }


def _render_plotly_chart(fig: go.Figure, height: int = 200):
    """Render Plotly figure as HTML in Mesop."""
    html_str = fig.to_html(
        include_plotlyjs='cdn',
        full_html=False,
        config={
            'displayModeBar': False,
            'staticPlot': False,
            'responsive': True,
        }
    )
    me.html(
        html_str,
        mode="sandboxed",
        style=me.Style(
            width="100%",
            height=height,
            border=me.Border.all(
                me.BorderSide(width=0, color="transparent", style="none")
            ),
        ),
    )


# =============================================================================
# RSI GAUGE CHART
# =============================================================================

def rsi_gauge_chart(rsi_value: Optional[float], height: int = 180):
    """
    Render RSI gauge chart.

    RSI ranges:
    - 0-30: Oversold (Green - Buy signal)
    - 30-70: Neutral (Gray)
    - 70-100: Overbought (Red - Sell signal)
    """
    if rsi_value is None:
        me.text("RSI 데이터 없음", style=me.Style(
            color=COLORS['text_secondary'],
            font_size=13,
            text_align='center',
        ))
        return

    # Determine color based on RSI value
    if rsi_value <= 30:
        bar_color = COLORS['bullish']
        status = "과매도"
    elif rsi_value >= 70:
        bar_color = COLORS['bearish']
        status = "과매수"
    else:
        bar_color = COLORS['neutral']
        status = "중립"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rsi_value,
        number={'suffix': '', 'font': {'size': 28, 'color': COLORS['text_primary']}},
        title={'text': f"RSI ({status})", 'font': {'size': 14, 'color': COLORS['text_secondary']}},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': COLORS['text_secondary'],
                'tickvals': [0, 30, 50, 70, 100],
                'ticktext': ['0', '30', '50', '70', '100'],
            },
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': COLORS['surface'],
            'borderwidth': 0,
            'steps': [
                {'range': [0, 30], 'color': _hex_to_rgba(COLORS['bullish'], 0.2)},
                {'range': [30, 70], 'color': _hex_to_rgba(COLORS['neutral'], 0.15)},
                {'range': [70, 100], 'color': _hex_to_rgba(COLORS['bearish'], 0.2)},
            ],
            'threshold': {
                'line': {'color': COLORS['text_primary'], 'width': 2},
                'thickness': 0.8,
                'value': rsi_value,
            },
        }
    ))

    fig.update_layout(**_get_chart_layout(height, margin=dict(l=30, r=30, t=50, b=10)))
    _render_plotly_chart(fig, height)


# =============================================================================
# SUPPORT/RESISTANCE LEVEL CHART
# =============================================================================

def support_resistance_chart(
    current_price: Optional[float],
    support_levels: Optional[List[float]],
    resistance_levels: Optional[List[float]],
    height: int = 220,
):
    """
    Render support and resistance levels as horizontal bar chart.

    - Green bars: Support levels (below current price)
    - Red bars: Resistance levels (above current price)
    - Blue line: Current price
    """
    if current_price is None:
        me.text("가격 데이터 없음", style=me.Style(
            color=COLORS['text_secondary'],
            font_size=13,
            text_align='center',
        ))
        return

    supports = support_levels or []
    resistances = resistance_levels or []

    if not supports and not resistances:
        me.text("지지/저항선 데이터 없음", style=me.Style(
            color=COLORS['text_secondary'],
            font_size=13,
            text_align='center',
        ))
        return

    # Prepare data
    all_prices = supports + resistances + [current_price]
    y_min = min(all_prices) * 0.95
    y_max = max(all_prices) * 1.05

    fig = go.Figure()

    # Add resistance levels (red)
    for i, level in enumerate(sorted(resistances, reverse=True)):
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[level, level],
            mode='lines',
            name=f'저항 ${level:,.0f}',
            line=dict(color=COLORS['bearish'], width=2, dash='dash'),
            showlegend=(i == 0),
        ))
        fig.add_annotation(
            x=1.05, y=level,
            text=f"${level:,.0f}",
            showarrow=False,
            font=dict(color=COLORS['bearish'], size=11),
            xanchor='left',
        )

    # Add support levels (green)
    for i, level in enumerate(sorted(supports, reverse=True)):
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[level, level],
            mode='lines',
            name=f'지지 ${level:,.0f}',
            line=dict(color=COLORS['bullish'], width=2, dash='dash'),
            showlegend=(i == 0),
        ))
        fig.add_annotation(
            x=1.05, y=level,
            text=f"${level:,.0f}",
            showarrow=False,
            font=dict(color=COLORS['bullish'], size=11),
            xanchor='left',
        )

    # Add current price line (blue, solid)
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[current_price, current_price],
        mode='lines',
        name=f'현재가 ${current_price:,.2f}',
        line=dict(color=COLORS['buy'], width=3),
    ))
    fig.add_annotation(
        x=1.05, y=current_price,
        text=f"${current_price:,.2f}",
        showarrow=False,
        font=dict(color=COLORS['buy'], size=12, weight='bold'),
        xanchor='left',
    )

    layout = _get_chart_layout(height, margin=dict(l=10, r=80, t=30, b=30))
    layout.update({
        'xaxis': {'visible': False, 'range': [0, 1.3]},
        'yaxis': {
            'range': [y_min, y_max],
            'tickformat': '$,.0f',
            'tickfont': {'size': 10, 'color': COLORS['text_secondary']},
            'gridcolor': COLORS['divider'],
            'gridwidth': 1,
        },
        'showlegend': True,
        'legend': {
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'center',
            'x': 0.5,
            'font': {'size': 10},
        },
    })
    fig.update_layout(**layout)
    _render_plotly_chart(fig, height)


# =============================================================================
# VALUATION BAR CHART (Fundamental)
# =============================================================================

def valuation_bar_chart(
    pe_ratio: Optional[float],
    pb_ratio: Optional[float],
    roe: Optional[float],
    revenue_growth: Optional[float],
    height: int = 200,
):
    """
    Render valuation metrics as horizontal bar chart.

    Compares key fundamental metrics with industry benchmarks.
    """
    metrics = []
    values = []
    colors = []

    # P/E Ratio (lower is better, but negative means no profit)
    if pe_ratio is not None:
        metrics.append('P/E')
        display_val = min(max(pe_ratio, -50), 100)  # Clamp for display
        values.append(display_val)
        if pe_ratio < 0:
            colors.append(COLORS['bearish'])  # Negative = loss
        elif pe_ratio < 20:
            colors.append(COLORS['bullish'])  # Good
        elif pe_ratio < 40:
            colors.append(COLORS['hold'])  # Moderate
        else:
            colors.append(COLORS['bearish'])  # High

    # P/B Ratio (lower is generally better)
    if pb_ratio is not None:
        metrics.append('P/B')
        values.append(min(pb_ratio, 20))  # Clamp for display
        if pb_ratio < 1:
            colors.append(COLORS['bullish'])
        elif pb_ratio < 3:
            colors.append(COLORS['hold'])
        else:
            colors.append(COLORS['bearish'])

    # ROE (higher is better, typically 15%+ is good)
    if roe is not None:
        metrics.append('ROE')
        roe_pct = roe * 100 if abs(roe) < 2 else roe  # Handle both decimal and percentage
        values.append(min(max(roe_pct, -50), 50))  # Clamp for display
        if roe_pct > 15:
            colors.append(COLORS['bullish'])
        elif roe_pct > 0:
            colors.append(COLORS['hold'])
        else:
            colors.append(COLORS['bearish'])

    # Revenue Growth (higher is better)
    if revenue_growth is not None:
        metrics.append('성장률')
        growth_pct = revenue_growth * 100 if abs(revenue_growth) < 5 else revenue_growth
        values.append(min(max(growth_pct, -50), 150))  # Clamp for display
        if growth_pct > 20:
            colors.append(COLORS['bullish'])
        elif growth_pct > 0:
            colors.append(COLORS['hold'])
        else:
            colors.append(COLORS['bearish'])

    if not metrics:
        me.text("밸류에이션 데이터 없음", style=me.Style(
            color=COLORS['text_secondary'],
            font_size=13,
            text_align='center',
        ))
        return

    fig = go.Figure(go.Bar(
        x=values,
        y=metrics,
        orientation='h',
        marker_color=colors,
        text=[f'{v:.1f}' for v in values],
        textposition='outside',
        textfont={'color': COLORS['text_primary'], 'size': 11},
    ))

    layout = _get_chart_layout(height, margin=dict(l=60, r=50, t=20, b=20))
    layout.update({
        'xaxis': {
            'showgrid': True,
            'gridcolor': COLORS['divider'],
            'zeroline': True,
            'zerolinecolor': COLORS['text_secondary'],
            'tickfont': {'size': 10},
        },
        'yaxis': {
            'tickfont': {'size': 12},
        },
        'bargap': 0.3,
    })
    fig.update_layout(**layout)
    _render_plotly_chart(fig, height)


# =============================================================================
# RISK GAUGE CHART
# =============================================================================

def risk_gauge_chart(
    risk_level: Optional[str],
    volatility: Optional[float],
    max_drawdown: Optional[float],
    height: int = 180,
):
    """
    Render risk level gauge chart.

    Risk levels: 낮음 (Low) -> 보통 (Moderate) -> 높음 (High) -> 매우 높음 (Very High)
    """
    # Convert risk level to numeric value
    risk_map = {
        'low': 1, '낮음': 1, '저위험': 1,
        'moderate': 2, 'medium': 2, '보통': 2, '중간': 2,
        'high': 3, '높음': 3, '고위험': 3,
        'very high': 4, 'very_high': 4, '매우 높음': 4, '매우높음': 4, '초고위험': 4,
    }

    risk_value = risk_map.get((risk_level or '').lower(), 2)

    # Determine color
    risk_colors = {
        1: COLORS['low_risk'],
        2: COLORS['moderate_risk'],
        3: COLORS['high_risk'],
        4: COLORS['very_high_risk'],
    }
    bar_color = risk_colors.get(risk_value, COLORS['neutral'])

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_value,
        number={'font': {'size': 1, 'color': 'rgba(0,0,0,0)'}},  # Hide number with transparent color
        title={'text': f"리스크: {risk_level or 'N/A'}", 'font': {'size': 14, 'color': COLORS['text_secondary']}},
        gauge={
            'axis': {
                'range': [0, 4],
                'tickwidth': 1,
                'tickcolor': COLORS['text_secondary'],
                'tickvals': [0.5, 1.5, 2.5, 3.5],
                'ticktext': ['낮음', '보통', '높음', '매우높음'],
            },
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': COLORS['surface'],
            'borderwidth': 0,
            'steps': [
                {'range': [0, 1], 'color': _hex_to_rgba(COLORS['low_risk'], 0.2)},
                {'range': [1, 2], 'color': _hex_to_rgba(COLORS['moderate_risk'], 0.2)},
                {'range': [2, 3], 'color': _hex_to_rgba(COLORS['high_risk'], 0.2)},
                {'range': [3, 4], 'color': _hex_to_rgba(COLORS['very_high_risk'], 0.2)},
            ],
            'threshold': {
                'line': {'color': bar_color, 'width': 3},
                'thickness': 0.9,
                'value': risk_value,
            },
        }
    ))

    fig.update_layout(**_get_chart_layout(height, margin=dict(l=30, r=30, t=50, b=10)))
    _render_plotly_chart(fig, height)


# =============================================================================
# VOLATILITY/DRAWDOWN BAR CHART
# =============================================================================

def risk_metrics_bar_chart(
    volatility: Optional[float],
    max_drawdown: Optional[float],
    beta: Optional[float],
    sharpe_ratio: Optional[float],
    height: int = 180,
):
    """
    Render risk metrics as bar chart.
    """
    metrics = []
    values = []
    colors = []

    # Volatility (lower is generally better for stability)
    if volatility is not None:
        metrics.append('변동성')
        vol_pct = volatility * 100 if volatility < 5 else volatility
        values.append(min(vol_pct, 150))
        if vol_pct < 20:
            colors.append(COLORS['low_risk'])
        elif vol_pct < 40:
            colors.append(COLORS['moderate_risk'])
        else:
            colors.append(COLORS['high_risk'])

    # Max Drawdown (negative value, closer to 0 is better)
    if max_drawdown is not None:
        metrics.append('최대낙폭')
        dd_pct = max_drawdown * 100 if abs(max_drawdown) < 2 else max_drawdown
        values.append(dd_pct)  # Keep negative
        if dd_pct > -20:
            colors.append(COLORS['low_risk'])
        elif dd_pct > -40:
            colors.append(COLORS['moderate_risk'])
        else:
            colors.append(COLORS['high_risk'])

    # Sharpe Ratio (higher is better, > 1 is good)
    if sharpe_ratio is not None:
        metrics.append('샤프비율')
        values.append(sharpe_ratio)
        if sharpe_ratio > 1:
            colors.append(COLORS['bullish'])
        elif sharpe_ratio > 0:
            colors.append(COLORS['hold'])
        else:
            colors.append(COLORS['bearish'])

    if not metrics:
        me.text("리스크 지표 데이터 없음", style=me.Style(
            color=COLORS['text_secondary'],
            font_size=13,
            text_align='center',
        ))
        return

    fig = go.Figure(go.Bar(
        x=values,
        y=metrics,
        orientation='h',
        marker_color=colors,
        text=[f'{v:.1f}%' if 'drawdown' in m.lower() or '변동' in m or '낙폭' in m else f'{v:.2f}' for v, m in zip(values, metrics)],
        textposition='outside',
        textfont={'color': COLORS['text_primary'], 'size': 11},
    ))

    layout = _get_chart_layout(height, margin=dict(l=70, r=50, t=20, b=20))
    layout.update({
        'xaxis': {
            'showgrid': True,
            'gridcolor': COLORS['divider'],
            'zeroline': True,
            'zerolinecolor': COLORS['text_secondary'],
            'tickfont': {'size': 10},
        },
        'yaxis': {
            'tickfont': {'size': 12},
        },
        'bargap': 0.3,
    })
    fig.update_layout(**layout)
    _render_plotly_chart(fig, height)


# =============================================================================
# SENTIMENT GAUGE CHART
# =============================================================================

def sentiment_gauge_chart(
    sentiment_score: Optional[float],
    sentiment_verdict: Optional[str],
    height: int = 180,
):
    """
    Render sentiment gauge chart.

    Sentiment score: -1 (very bearish) to 1 (very bullish) or 0 to 1
    """
    if sentiment_score is None:
        me.text("감성 데이터 없음", style=me.Style(
            color=COLORS['text_secondary'],
            font_size=13,
            text_align='center',
        ))
        return

    # Normalize score to 0-100 for gauge display
    if -1 <= sentiment_score <= 1:
        normalized = (sentiment_score + 1) * 50  # -1~1 -> 0~100
    else:
        normalized = sentiment_score * 100 if sentiment_score <= 1 else sentiment_score

    normalized = max(0, min(100, normalized))

    # Determine color
    if normalized >= 60:
        bar_color = COLORS['bullish']
    elif normalized <= 40:
        bar_color = COLORS['bearish']
    else:
        bar_color = COLORS['neutral']

    verdict_text = sentiment_verdict or ('강세' if normalized >= 60 else '약세' if normalized <= 40 else '중립')

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=normalized,
        number={'suffix': '', 'font': {'size': 24, 'color': COLORS['text_primary']}},
        title={'text': f"시장 심리 ({verdict_text})", 'font': {'size': 14, 'color': COLORS['text_secondary']}},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': COLORS['text_secondary'],
                'tickvals': [0, 25, 50, 75, 100],
                'ticktext': ['약세', '', '중립', '', '강세'],
            },
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': COLORS['surface'],
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': _hex_to_rgba(COLORS['bearish'], 0.2)},
                {'range': [40, 60], 'color': _hex_to_rgba(COLORS['neutral'], 0.15)},
                {'range': [60, 100], 'color': _hex_to_rgba(COLORS['bullish'], 0.2)},
            ],
            'threshold': {
                'line': {'color': COLORS['text_primary'], 'width': 2},
                'thickness': 0.8,
                'value': normalized,
            },
        }
    ))

    fig.update_layout(**_get_chart_layout(height, margin=dict(l=30, r=30, t=50, b=10)))
    _render_plotly_chart(fig, height)
