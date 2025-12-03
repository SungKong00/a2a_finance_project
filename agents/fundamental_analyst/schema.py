from pydantic import BaseModel, Field

class FundamentalAnalysisData(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol")
    market_cap: float = Field(..., description="Market capitalization")
    pe_ratio: float = Field(..., description="Price-to-Earnings ratio")
    pb_ratio: float = Field(..., description="Price-to-Book ratio")
    revenue_growth: float = Field(..., description="Revenue growth rate (percentage)")
    roe: float = Field(..., description="Return on Equity (percentage)")
    valuation_verdict: str = Field(..., description="Valuation assessment: Undervalued, Fairly Valued, or Overvalued")
    analysis_content: str = Field(..., description="Full text analysis and fundamental verdict")
