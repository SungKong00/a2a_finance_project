from pydantic import BaseModel, Field

class RiskAnalysisData(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol")
    risk_level: str = Field(..., description="Overall risk level: Low, Moderate, High, or Very High")
    beta: float = Field(..., description="Beta coefficient vs market")
    volatility: float = Field(..., description="Annualized volatility (percentage)")
    max_drawdown: float = Field(..., description="Maximum drawdown (percentage)")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    analysis_content: str = Field(..., description="Full text analysis and risk verdict")
