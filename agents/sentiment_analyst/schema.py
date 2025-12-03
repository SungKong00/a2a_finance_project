from typing import List
from pydantic import BaseModel, Field

class SentimentAnalysisData(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol")
    sentiment_score: float = Field(..., description="Sentiment score (e.g., 0.0 to 1.0 or -1 to 1)")
    sentiment_verdict: str = Field(..., description="Overall sentiment: Bullish, Bearish, or Neutral")
    analyst_consensus: str = Field(..., description="Summary of analyst ratings (e.g., Strong Buy, Hold)")
    top_headlines: List[str] = Field(..., description="List of top news headlines affecting sentiment")
    analysis_content: str = Field(..., description="Full text analysis and sentiment verdict")
