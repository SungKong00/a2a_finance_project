"""
Mock Response Manager for Development

Saves API responses to JSON files for later replay.
Enables UI development without making actual API calls.

Usage:
    1. Set USE_MOCK_RESPONSES=false (default) to make real API calls
       - Responses are automatically saved to mock_data/
    2. Set USE_MOCK_RESPONSES=true to use saved responses
       - No API calls are made, responses are loaded from mock_data/

Environment Variables:
    USE_MOCK_RESPONSES: "true" to enable mock mode, "false" for real API (default)
    MOCK_DATA_DIR: Directory to save/load mock data (default: ./mock_data)
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class MockResponseManager:
    """Manages saving and loading mock API responses."""

    def __init__(self, mock_data_dir: str = None):
        self.mock_data_dir = Path(mock_data_dir or os.getenv('MOCK_DATA_DIR', './mock_data'))
        self.mock_data_dir.mkdir(parents=True, exist_ok=True)
        self.use_mock = os.getenv('USE_MOCK_RESPONSES', 'false').lower() == 'true'

        if self.use_mock:
            print(f"[MockManager] MOCK MODE ENABLED - Loading responses from {self.mock_data_dir}")
        else:
            print(f"[MockManager] REAL MODE - Responses will be saved to {self.mock_data_dir}")

    def _get_cache_key(self, ticker: str, agent_name: str) -> str:
        """Generate a cache key for a specific request."""
        return f"{ticker.upper()}_{agent_name}"

    def _get_cache_path(self, ticker: str, agent_name: str) -> Path:
        """Get the file path for a cached response."""
        key = self._get_cache_key(ticker, agent_name)
        return self.mock_data_dir / f"{key}.json"

    def save_response(self, ticker: str, agent_name: str, response: Any) -> None:
        """Save an API response to a JSON file."""
        cache_path = self._get_cache_path(ticker, agent_name)

        data = {
            "ticker": ticker.upper(),
            "agent_name": agent_name,
            "timestamp": datetime.now().isoformat(),
            "response": response
        }

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[MockManager] Saved response: {cache_path}")

    def load_response(self, ticker: str, agent_name: str) -> Optional[Any]:
        """Load a saved response from JSON file."""
        cache_path = self._get_cache_path(ticker, agent_name)

        if not cache_path.exists():
            print(f"[MockManager] No cached response found: {cache_path}")
            return None

        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"[MockManager] Loaded cached response: {cache_path} (saved at {data.get('timestamp', 'unknown')})")
        return data.get("response")

    def has_cached_response(self, ticker: str, agent_name: str) -> bool:
        """Check if a cached response exists."""
        return self._get_cache_path(ticker, agent_name).exists()

    def list_cached_responses(self) -> list[dict]:
        """List all cached responses."""
        cached = []
        for file_path in self.mock_data_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                cached.append({
                    "file": file_path.name,
                    "ticker": data.get("ticker"),
                    "agent_name": data.get("agent_name"),
                    "timestamp": data.get("timestamp")
                })
            except Exception as e:
                print(f"[MockManager] Error reading {file_path}: {e}")
        return cached

    def clear_cache(self, ticker: str = None) -> int:
        """Clear cached responses. If ticker is provided, only clear that ticker's cache."""
        count = 0
        pattern = f"{ticker.upper()}_*.json" if ticker else "*.json"

        for file_path in self.mock_data_dir.glob(pattern):
            file_path.unlink()
            count += 1
            print(f"[MockManager] Deleted: {file_path}")

        return count

    def save_full_analysis(self, ticker: str, all_responses: dict[str, Any]) -> None:
        """Save all 4 agent responses as a single analysis bundle."""
        bundle_path = self.mock_data_dir / f"{ticker.upper()}_FULL_ANALYSIS.json"

        data = {
            "ticker": ticker.upper(),
            "timestamp": datetime.now().isoformat(),
            "agents": all_responses
        }

        with open(bundle_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[MockManager] Saved full analysis bundle: {bundle_path}")

    def load_full_analysis(self, ticker: str) -> Optional[dict[str, Any]]:
        """Load a full analysis bundle."""
        bundle_path = self.mock_data_dir / f"{ticker.upper()}_FULL_ANALYSIS.json"

        if not bundle_path.exists():
            # Try loading individual files
            agents = ["technical_analyst", "fundamental_analyst", "sentiment_analyst", "risk_assessor"]
            responses = {}

            for agent in agents:
                response = self.load_response(ticker, agent)
                if response:
                    responses[agent] = response

            if responses:
                print(f"[MockManager] Loaded {len(responses)} individual agent responses for {ticker}")
                return responses

            print(f"[MockManager] No cached analysis found for {ticker}")
            return None

        with open(bundle_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"[MockManager] Loaded full analysis bundle: {bundle_path} (saved at {data.get('timestamp', 'unknown')})")
        return data.get("agents")


# Global instance
_mock_manager: Optional[MockResponseManager] = None


def get_mock_manager() -> MockResponseManager:
    """Get the global MockResponseManager instance."""
    global _mock_manager
    if _mock_manager is None:
        _mock_manager = MockResponseManager()
    return _mock_manager


def is_mock_mode() -> bool:
    """Check if mock mode is enabled."""
    return get_mock_manager().use_mock
