import os
from tavily import TavilyClient
import yfinance as yf
from typing import Dict, Any
import json

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def get_stock_metrics(ticker: str) -> Dict[str, Any]:
    """Fetch key stock metrics using yfinance"""
    from app_logging import log_tool_use
    log_tool_use("yfinance", {"ticker": ticker})
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Handle cases where data is None
    def safe_get(key, default='N/A'):
        val = info.get(key)
        return default if val is None else val

    return {
        'current_price': safe_get('currentPrice'),
        'pe_ratio': safe_get('trailingPE'),
        'market_cap': safe_get('marketCap'),
        '52_week_high': safe_get('fiftyTwoWeekHigh'),
        '52_week_low': safe_get('fiftyTwoWeekLow'),
        'dividend_yield': safe_get('dividendYield'),
        'volume': safe_get('volume', 0),
        'avg_volume': safe_get('averageVolume', 0),
        'beta': safe_get('beta')
    }

def get_stock_news(ticker: str) -> Dict[str, Any]:
    """Search for recent news about the stock using Tavily"""
    from app_logging import log_tool_use
    log_tool_use("Tavily News Search", {"ticker": ticker})
    if not TAVILY_API_KEY:
        return {"error": "Tavily API key not configured"}
        
    results = tavily.search(
        query=f"{ticker} stock news",
        search_depth="basic",
        include_raw_content=True,
        max_results=5
    )
    
    return {
        'news': [{
            'title': r.get('title'),
            'url': r.get('url'),
            'description': r.get('content'),
            'date': r.get('published_date')
        } for r in results.get('results', [])]
    }

def get_executive_changes(ticker: str) -> Dict[str, Any]:
    """Search for executive changes using Tavily"""
    if not TAVILY_API_KEY:
        return {"error": "Tavily API key not configured"}
        
    results = tavily.search(
        query=f"{ticker} CEO OR CTO OR CFO OR CRO joined OR left",
        search_depth="basic",
        include_raw_content=True,
        max_results=3
    )
    
    return {
        'executive_changes': [{
            'title': r.get('title'),
            'url': r.get('url'),
            'description': r.get('content'),
            'date': r.get('published_date')
        } for r in results.get('results', [])]
    }

def get_stock_research(ticker: str) -> str:
    """Generate comprehensive research report"""
    try:
        metrics = get_stock_metrics(ticker)
        news = get_stock_news(ticker)
        executives = get_executive_changes(ticker)
        
        report = f"Stock Research for {ticker}\n\n"
        report += "Key Metrics:\n"
        report += f"- Current Price: ${metrics.get('current_price', 'N/A')}\n"
        report += f"- P/E Ratio: {metrics.get('pe_ratio', 'N/A')}\n"
        report += f"- Market Cap: ${metrics.get('market_cap', 'N/A'):,}\n"
        report += f"- 52 Week Range: ${metrics.get('52_week_low', 'N/A')} - ${metrics.get('52_week_high', 'N/A')}\n"
        report += f"- Volume: {metrics.get('volume', 'N/A'):,} (Avg: {metrics.get('avg_volume', 'N/A'):,})\n"
        
        if news.get('news'):
            report += "\nRecent News:\n"
            for item in news['news']:
                report += f"- {item['title']} ({item['date']})\n"
                report += f"  {item['description']}\n"
                report += f"  Source: {item['url']}\n\n"
        
        if executives.get('executive_changes'):
            report += "\nExecutive Changes:\n"
            for change in executives['executive_changes']:
                report += f"- {change['title']}\n"
                report += f"  {change['description']}\n"
                report += f"  Source: {change['url']}\n\n"
        
        return report
    except Exception as e:
        return f"Error generating research report: {str(e)}"
