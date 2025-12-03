from typing import List
from pydantic import BaseModel, Field

class TechnicalAnalysisData(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol")
    current_price: float = Field(..., description="Current market price of the stock")
    trend: str = Field(..., description="Overall trend: Bullish, Bearish, or Neutral")
    rsi: float = Field(..., description="Relative Strength Index value")
    macd_signal: str = Field(..., description="MACD signal interpretation (e.g., Bullish Crossover)")
    support_levels: List[float] = Field(..., description="List of key support price levels")
    resistance_levels: List[float] = Field(..., description="List of key resistance price levels")
    analysis_content: str = Field(..., description="Full text analysis and trading recommendation")
