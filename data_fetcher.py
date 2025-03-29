import os
import yfinance as yf
from typing import Dict, Any, Optional
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def get_stock_symbol(company_name: str, country: str = "") -> Optional[str]:
    """
    Use LLM to find the stock symbol for a company name
    Returns format like "AAPL" or "TATA.NS" for Indian stocks
    """
    if not client or not OPENAI_API_KEY:
        logging.error("OpenAI client not configured")
        return None

    prompt = f"""Given the company name "{company_name}" {f"based in {country}" if country else ""}, 
    return ONLY the most likely stock ticker symbol in the format required by Yahoo Finance.
    
    Important Examples:
    - Apple → AAPL
    - Bharti Airtel → BHARTIARTL.NS
    - Tata Motors → TATAMOTORS.NS  
    - Reliance Industries → RELIANCE.NS
    
    Rules:
    1. For Indian stocks: 
       - Bharti Airtel → BHARTIARTL.NS
       - Tata Motors → TATAMOTORS.NS
       - Always verify exact symbol format
    2. For US stocks: just the symbol (e.g. AAPL)
    3. For others: use appropriate exchange suffix
    4. Return ONLY the symbol, no other text
    5. If unsure, return BLANK
    
    Verify symbol is correct before returning."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temperature for more deterministic responses
            max_tokens=10
        )
        symbol = response.choices[0].message.content.strip()

        # Clean and validate the symbol
        symbol = symbol.strip().upper()
        if not symbol or " " in symbol:
            logging.error(f"Invalid symbol returned: {symbol}")
            return None
            
        return symbol
    except Exception as e:
        logging.error(f"LLM symbol lookup error: {str(e)}")
        return None

def get_stock_metrics(ticker: str) -> Dict[str, Any]:
    """Fetch key stock metrics with enhanced error handling"""
    try:
        # First check if ticker is supported
        stock = yf.Ticker(ticker)
        if not stock.info:
            return {'error': f"Ticker {ticker} not found or not supported by Yahoo Finance"}
            
        info = stock.info
        
        # Handle Indian stocks differently
        is_indian = ticker.endswith('.NS') or ticker.endswith('.BO')
        
        metrics = {
            'current_price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
            'pe_ratio': info.get('trailingPE', info.get('forwardPE', 'N/A')),
            'market_cap': info.get('marketCap', 'N/A'),
            '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
            'volume': info.get('volume', 'N/A'),
            'avg_volume': info.get('averageVolume', 'N/A'),
            'currency': 'INR' if is_indian else info.get('currency', 'USD')
        }
        
        return metrics
        
    except Exception as e:
        logging.error(f"yfinance error for {ticker}: {str(e)}")
        return {'error': f"Failed to fetch metrics: {str(e)}"}

def get_stock_news(ticker: str) -> Dict[str, Any]:
    """Search for recent news about the stock"""
    if not TAVILY_API_KEY:
        return {"error": "Tavily API key not configured"}
        
    try:
        from tavily import TavilyClient
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
        
        results = tavily.search(
            query=f"{ticker} stock news",
            search_depth="basic",
            max_results=5
        )
        
        return {
            'news': [{
                'title': r.get('title', 'No title'),
                'url': r.get('url', '#'),
                'description': r.get('content', 'No description available')
            } for r in results.get('results', [])]
        }
    except Exception as e:
        logging.error(f"News search error for {ticker}: {str(e)}")
        return {'error': f"News unavailable: {str(e)}"}

def get_stock_research(ticker: str) -> Dict[str, Any]:
    """Get all research data for a stock"""
    return {
        'metrics': get_stock_metrics(ticker),
        'news': get_stock_news(ticker)
    }
