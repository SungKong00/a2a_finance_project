"""
Metric Gauge Component

Visual gauge component for displaying numeric metrics with
colored progress bars indicating value ranges.
"""

import mesop as me
from typing import Optional

from styles.stock_styles import (
    COLORS,
    GAUGE_CONTAINER_STYLE,
    GAUGE_LABEL_ROW_STYLE,
    GAUGE_TRACK_STYLE,
    gauge_fill_style,
    METRIC_CONFIG,
    get_metric_color,
)


def metric_gauge(
    metric_name: str,
    value: float,
    label: Optional[str] = None,
    show_range: bool = False,
):
    """
    Render a metric gauge with colored progress bar.

    Args:
        metric_name: The metric identifier (e.g., 'rsi', 'beta', 'pe_ratio')
        value: The numeric value to display
        label: Optional custom label (defaults to config label)
        show_range: Whether to show the good range indicators
    """
    config = METRIC_CONFIG.get(metric_name, {})
    display_label = label or config.get('label', metric_name.upper())
    min_val = config.get('min', 0)
    max_val = config.get('max', 100)

    # Calculate percentage
    range_size = max_val - min_val
    if range_size > 0:
        percentage = ((value - min_val) / range_size) * 100
    else:
        percentage = 50

    # Get color based on value
    color = get_metric_color(metric_name, value)

    with me.box(style=GAUGE_CONTAINER_STYLE):
        # Label row
        label_row_style = me.Style(
            display='flex',
            flex_direction='row',
            justify_content='space-between',
            font_size=13,
            margin=me.Margin(bottom=4),
        )

        with me.box(style=label_row_style):
            me.text(display_label, style=me.Style(color=COLORS['text_secondary']))
            me.text(
                f'{value:.2f}' if isinstance(value, float) else str(value),
                style=me.Style(color=color, font_weight='500'),
            )

        # Gauge track
        with me.box(style=GAUGE_TRACK_STYLE):
            me.box(style=gauge_fill_style(percentage, color))

        # Optional range indicators
        if show_range and config.get('good_range'):
            _render_range_indicators(config, min_val, max_val)


def _render_range_indicators(config: dict, min_val: float, max_val: float):
    """Render good range indicators below the gauge."""
    good_min, good_max = config.get('good_range', (0, 100))
    range_size = max_val - min_val

    if range_size <= 0:
        return

    # Calculate positions as percentages
    good_start = ((good_min - min_val) / range_size) * 100
    good_end = ((good_max - min_val) / range_size) * 100

    range_container_style = me.Style(
        position='relative',
        height=4,
        margin=me.Margin(top=4),
    )

    range_indicator_style = me.Style(
        position='absolute',
        left=f'{good_start}%',
        width=f'{good_end - good_start}%',
        height=4,
        background=COLORS['bullish'] + '40',  # 40% opacity
        border_radius=2,
    )

    with me.box(style=range_container_style):
        me.box(style=range_indicator_style)


def mini_gauge(value: float, max_value: float = 100, color: Optional[str] = None):
    """
    Simple mini gauge without labels.

    Args:
        value: Current value
        max_value: Maximum value for the gauge
        color: Optional custom color
    """
    percentage = (value / max_value) * 100 if max_value > 0 else 0
    fill_color = color or COLORS['accent']

    mini_track_style = me.Style(
        height=4,
        background=COLORS['divider'],
        border_radius=2,
        overflow='hidden',
        width=60,
    )

    mini_fill_style = me.Style(
        height=4,
        width=f'{min(100, max(0, percentage))}%',
        background=fill_color,
        border_radius=2,
    )

    with me.box(style=mini_track_style):
        me.box(style=mini_fill_style)


def confidence_gauge(confidence: float, label: str = "Confidence"):
    """
    Special gauge for confidence scores (0-100%).

    Args:
        confidence: Confidence value (0-100)
        label: Label text
    """
    # Determine color based on confidence level
    if confidence >= 80:
        color = COLORS['bullish']
    elif confidence >= 60:
        color = COLORS['moderate_risk']
    elif confidence >= 40:
        color = COLORS['hold']
    else:
        color = COLORS['bearish']

    container_style = me.Style(
        display='flex',
        flex_direction='column',
        gap=4,
    )

    with me.box(style=container_style):
        # Label and value
        header_style = me.Style(
            display='flex',
            justify_content='space-between',
            align_items='center',
        )

        with me.box(style=header_style):
            me.text(label, style=me.Style(
                font_size=12,
                color=COLORS['text_secondary'],
            ))
            me.text(f'{confidence:.0f}%', style=me.Style(
                font_size=12,
                font_weight='bold',
                color=color,
            ))

        # Gauge
        track_style = me.Style(
            height=6,
            background=COLORS['divider'],
            border_radius=3,
            overflow='hidden',
        )

        fill_style = me.Style(
            height=6,
            width=f'{min(100, max(0, confidence))}%',
            background=color,
            border_radius=3,
        )

        with me.box(style=track_style):
            me.box(style=fill_style)
