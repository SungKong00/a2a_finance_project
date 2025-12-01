from mcp.server.fastmcp import FastMCP
import yfinance as yf
import pandas as pd
import json

# Initialize FastMCP
mcp = FastMCP("stock-data-server")

@mcp.tool()
def get_ticker(query: str) -> str:
    """
    Search for a valid stock ticker symbol based on a company name or keyword.
    
    Args:
        query: The company name (e.g., "Samsung", "Apple") or keyword.
        
    Returns:
        The best matching ticker symbol (e.g., "005930.KS", "AAPL"). 
        Returns "NOT_FOUND" if no match is found.
    """
    try:
        # yfinance doesn't have a direct search API that returns tickers easily without extra libs.
        # However, Ticker object can be used if the user inputs a valid ticker.
        # For better search, we might need a dedicated search tool or mapping.
        # For this MVP, we will try to handle common cases or rely on exact input if search fails.
        
        # Simplified Logic: If it looks like a ticker, return it. 
        # In a real scenario, we would use a search API (like Yahoo Finance Search endpoint).
        # Here we assume the user might input "AAPL" or "005930.KS".
        # We can add a small dictionary for common Korean stocks for better UX.
        
        common_map = {
            "삼성전자": "005930.KS",
            "현대차": "005380.KS",
            "네이버": "035420.KS",
            "카카오": "035720.KS",
            "하이닉스": "000660.KS",
            "애플": "AAPL",
            "테슬라": "TSLA",
            "엔비디아": "NVDA",
            "구글": "GOOGL",
            "마이크로소프트": "MSFT"
        }
        
        if query in common_map:
            return common_map[query]
            
        # If not in map, return as uppercase, assuming user knows the ticker
        # Or we could try to hit an external search API here.
        return query.upper()
        
    except Exception as e:
        return f"ERROR: {str(e)}"

@mcp.tool()
def get_stock_data(ticker: str) -> str:
    """
    Fetch comprehensive stock data including fundamentals, market sentiment, and news.
    
    Args:
        ticker: The stock ticker symbol (e.g., "AAPL", "005930.KS").
        
    Returns:
        A JSON string containing price, per, pbr, roe, vix, target_price, and news.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 1. Fundamental Data
        price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        currency = info.get('currency', 'USD')
        per = info.get('trailingPE', None)
        pbr = info.get('priceToBook', None)
        roe = info.get('returnOnEquity', None)
        
        # 2. Market Sentiment (VIX)
        # VIX is valid for US market context mostly, but good for global sentiment
        try:
            vix_ticker = yf.Ticker("^VIX")
            vix_close = vix_ticker.history(period="1d")['Close'].iloc[-1]
        except:
            vix_close = None
            
        # 3. Consensus
        target_price = info.get('targetMeanPrice', None)
        recommendation = info.get('recommendationKey', 'none')
        
        # 4. News (Top 3)
        news_list = []
        # yfinance news often returns a list of dicts
        if hasattr(stock, 'news'):
            for n in stock.news[:3]:
                news_list.append({
                    "title": n.get('title'),
                    "link": n.get('link'),
                    "publisher": n.get('publisher')
                })
        
        result = {
            "ticker": ticker,
            "price": price,
            "currency": currency,
            "fundamentals": {
                "PER": per,
                "PBR": pbr,
                "ROE": roe
            },
            "market_sentiment": {
                "VIX": round(vix_close, 2) if vix_close else "N/A",
                "target_price": target_price,
                "recommendation": recommendation
            },
            "recent_news": news_list
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Run the server
    mcp.run()
