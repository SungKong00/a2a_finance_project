"""
JSON Parser Utility for Stock Analysis Responses

Extracts and parses JSON blocks from agent markdown responses.
Each agent returns markdown analysis + JSON block at the end.
"""

import json
import re
from typing import Any


def extract_json_from_response(response_text: str) -> dict[str, Any] | None:
    """
    Extract JSON block from agent response.

    Agents return responses like:
    ```
    [Markdown analysis...]

    ```json
    { "ticker": "AAPL", ... }
    ```
    ```

    Args:
        response_text: Full agent response text

    Returns:
        Parsed JSON dict or None if not found
    """
    if not response_text:
        return None

    # Pattern to match ```json ... ``` blocks
    json_pattern = r'```json\s*([\s\S]*?)\s*```'
    matches = re.findall(json_pattern, response_text)

    if not matches:
        # Try without json tag (just ``` ... ```)
        json_pattern = r'```\s*(\{[\s\S]*?\})\s*```'
        matches = re.findall(json_pattern, response_text)

    if matches:
        # Get the last JSON block (most likely the structured data)
        json_str = matches[-1].strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try to fix common JSON issues
            json_str = _fix_json_string(json_str)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None

    return None


def _fix_json_string(json_str: str) -> str:
    """Fix common JSON formatting issues."""
    # Remove trailing commas before ] or }
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    # Replace single quotes with double quotes
    json_str = json_str.replace("'", '"')
    return json_str


def identify_agent_type(json_data: dict[str, Any]) -> str | None:
    """
    Identify which agent type produced this JSON data.

    Returns: 'technical' | 'fundamental' | 'sentiment' | 'risk' | None
    """
    if not json_data:
        return None

    # Technical Analyst markers
    if 'rsi' in json_data or 'macd' in json_data or 'support_levels' in json_data:
        return 'technical'

    # Fundamental Analyst markers
    if 'pe_ratio' in json_data or 'roe' in json_data or 'valuation' in json_data:
        return 'fundamental'

    # Sentiment Analyst markers
    if 'sentiment_score' in json_data or 'sentiment_verdict' in json_data:
        return 'sentiment'

    # Risk Assessor markers
    if 'risk_level' in json_data or 'beta' in json_data or 'sharpe_ratio' in json_data:
        return 'risk'

    return None


def aggregate_analysis(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Aggregate responses from all 4 agents into a unified structure.

    Args:
        messages: List of message dicts with 'content' field

    Returns:
        Aggregated analysis dict:
        {
            'ticker': 'AAPL',
            'technical': {...},
            'fundamental': {...},
            'sentiment': {...},
            'risk': {...},
        }
    """
    result = {
        'ticker': None,
        'technical': None,
        'fundamental': None,
        'sentiment': None,
        'risk': None,
    }

    for message in messages:
        content = message.get('content', '')
        if isinstance(content, list):
            # Handle content as list of parts
            content = ' '.join(
                str(part) if isinstance(part, str) else str(part.get('text', ''))
                for part in content
            )

        json_data = extract_json_from_response(str(content))
        if json_data:
            agent_type = identify_agent_type(json_data)
            if agent_type and agent_type in result:
                result[agent_type] = json_data
                if json_data.get('ticker') and not result['ticker']:
                    result['ticker'] = json_data['ticker']

    return result


def parse_message_content(message_content: list[tuple[Any, str]]) -> dict[str, Any] | None:
    """
    Parse message content from StateMessage format.

    StateMessage.content is list of (content_part, media_type) tuples.

    Args:
        message_content: List of (content, media_type) tuples

    Returns:
        Extracted JSON data or None
    """
    for content_part, media_type in message_content:
        if media_type in ('text/plain', 'text/markdown'):
            json_data = extract_json_from_response(str(content_part))
            if json_data:
                return json_data
        elif isinstance(content_part, dict):
            # Already structured data
            if 'ticker' in content_part:
                return content_part

    return None


def get_analysis_from_messages(messages: list) -> dict[str, Any]:
    """
    Extract all analysis data from a list of StateMessage objects.

    Args:
        messages: List of StateMessage objects

    Returns:
        Aggregated analysis dict
    """
    result = {
        'ticker': None,
        'technical': None,
        'fundamental': None,
        'sentiment': None,
        'risk': None,
    }

    for message in messages:
        if hasattr(message, 'content'):
            # Handle StateMessage
            json_data = parse_message_content(message.content)
        elif isinstance(message, dict):
            # Handle dict
            content = message.get('content', [])
            if isinstance(content, list) and len(content) > 0:
                json_data = parse_message_content(content)
            else:
                json_data = extract_json_from_response(str(content))
        else:
            continue

        if json_data:
            agent_type = identify_agent_type(json_data)
            if agent_type and agent_type in result:
                result[agent_type] = json_data
                if json_data.get('ticker') and not result['ticker']:
                    result['ticker'] = json_data['ticker']

    return result


def has_analysis_data(analysis: dict[str, Any]) -> bool:
    """Check if analysis dict contains any actual data."""
    return any([
        analysis.get('technical'),
        analysis.get('fundamental'),
        analysis.get('sentiment'),
        analysis.get('risk'),
    ])
