"""Configure logging first"""
from app_logging import setup_logging
setup_logging()
import logging
import streamlit as st
from main import StockDebateSystem
from data_fetcher import get_stock_metrics, get_stock_news, get_stock_symbol
import asyncio
import yfinance as yf
import os
import json
import time

st.set_page_config(page_title="Stock Analysis AI", layout="wide")

# Initialize session state
if 'result' not in st.session_state:
    st.session_state.result = None
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'metrics' not in st.session_state:
    st.session_state.metrics = None
if 'news' not in st.session_state:
    st.session_state.news = None

def format_metric(value, ticker, is_currency=True):
    """Format metrics with proper currency symbol"""
    if value in ['N/A', None]:
        return "N/A"
    try:
        if isinstance(value, str):
            value = float(value.replace('$','').replace(',',''))
        prefix = "₹" if ticker.endswith(('.NS','.BO')) else "$"
        if is_currency:
            return f"{prefix}{value:,.2f}"
        return f"{value:,.2f}"
    except (ValueError, TypeError):
        return str(value)

# API Key Inputs
with st.sidebar:
    st.header("API Configuration")
    openai_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
    tavily_key = st.text_input("Tavily API Key", value=os.getenv("TAVILY_API_KEY", ""), type="password")
    
    st.header("About")
    st.write("AI agents debate stock investment decisions.")
    st.warning("Note: Not financial advice.")

async def run_analysis(ticker: str):
    """Run stock analysis and update UI"""
    if not openai_key or not tavily_key:
        st.error("Please enter both API keys")
        return
        
    os.environ["OPENAI_API_KEY"] = openai_key
    os.environ["TAVILY_API_KEY"] = tavily_key
    
    # Step 1: Fetch metrics
    with st.status(f"Fetching metrics for {ticker}..."):
        st.session_state.metrics = get_stock_metrics(ticker)
        if st.session_state.metrics.get('error'):
            st.error("Failed to fetch metrics")
            return

    # Step 2: Fetch news
    with st.status(f"Fetching news for {ticker}..."):
        st.session_state.news = get_stock_news(ticker)
        if st.session_state.news.get('error'):
            st.warning("News unavailable")

    # Step 3: Run analysis
    with st.status(f"Analyzing {ticker}..."):
        system = StockDebateSystem()
        result = await system.analyze_stock(ticker)
        st.session_state.result = result
        st.session_state.conversation = result['messages']

# UI Layout
st.title("Stock Analysis AI")
col1, col2 = st.columns(2)
with col1:
    company = st.text_input("Enter company name:", "Apple")
with col2:
    country = st.text_input("Country (optional):", "US")

if st.button("Analyze"):
    try:
        with st.spinner("Looking up stock symbol..."):
            ticker = get_stock_symbol(company, country)
            print (f"LLM response - step 2: {ticker}")  # Debugging line
            if not ticker:
                st.error("Could not determine stock symbol")
                st.stop()
            
            st.session_state.ticker = ticker
            st.success(f"Found symbol: {ticker}")
        asyncio.run(run_analysis(st.session_state.ticker))
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")

if st.session_state.metrics and hasattr(st.session_state, 'ticker'):
    st.header("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Price", format_metric(st.session_state.metrics.get('current_price'), st.session_state.ticker))
        st.metric("P/E Ratio", format_metric(st.session_state.metrics.get('pe_ratio'), st.session_state.ticker, False))
    with col2:
        st.metric("Market Cap", format_metric(st.session_state.metrics.get('market_cap'), st.session_state.ticker))
        st.metric("Volume", format_metric(st.session_state.metrics.get('volume', 0), st.session_state.ticker, False))
    with col3:
        low = st.session_state.metrics.get('52_week_low')
        high = st.session_state.metrics.get('52_week_high')
        range_str = f"{format_metric(low, st.session_state.ticker, False)} - {format_metric(high, st.session_state.ticker, False)}" if low != 'N/A' and high != 'N/A' else 'N/A'
        st.metric("52 Week Range", range_str)
        st.metric("Avg Volume", format_metric(st.session_state.metrics.get('avg_volume', 0), st.session_state.ticker, False))

if st.session_state.news and st.session_state.news.get('news'):
    st.header("Recent News")
    for item in st.session_state.news['news'][:5]:
        date = item.get('date') or 'Date not available'
        st.markdown(f"**{item['title']}**")
        st.caption(f"[Source]({item['url']}) | {date}")
        with st.expander("Read more"):
            st.write(item.get('description', 'No description available'))

if st.session_state.result:
    st.header("Agent Discussion")
    for msg in st.session_state.conversation:
        avatar = "🟢" if "Bullish" in msg['role'] else "🔴"
        with st.chat_message(msg['role'], avatar=avatar):
            st.write(msg['content'])

    st.header("Final Recommendation")
    st.info(st.session_state.result['conclusion'])
