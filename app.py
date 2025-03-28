import streamlit as st
from main import StockDebateSystem
from data_fetcher import get_stock_metrics, get_stock_news
import asyncio

st.set_page_config(page_title="Stock Analysis AI", layout="wide")

# Initialize session state
if 'result' not in st.session_state:
    st.session_state.result = None
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# API Key Inputs
with st.sidebar:
    st.header("API Configuration")
    openai_key = st.text_input("OpenAI API Key", type="password")
    tavily_key = st.text_input("Tavily API Key", type="password")
    
    st.header("About")
    st.write("""
    This app analyzes stocks using AI agents with opposing views.
    The Bullish Agent looks for growth potential while the Bearish Agent
    identifies risks.
    """)
    st.warning("Note: This is not financial advice. Do your own research.")

async def run_analysis(ticker: str):
    """Run stock analysis and update UI"""
    if not openai_key or not tavily_key:
        st.error("Please enter both API keys")
        return
        
    # Set API keys in environment
    import os
    os.environ["OPENAI_API_KEY"] = openai_key
    os.environ["TAVILY_API_KEY"] = tavily_key
    
    # Handle Indian stocks by adding exchange suffix if needed
    if not any(ticker.endswith(suffix) for suffix in ['.NS', '.BO']):
        ticker += '.NS'  # Default to NSE if no suffix provided
    
    system = StockDebateSystem()
    with st.spinner(f"Analyzing {ticker}..."):
        result = await system.analyze_stock(ticker)
        st.session_state.result = result
        st.session_state.conversation = result['messages']
    return result

# UI Layout
st.title("Stock Analysis AI")
ticker = st.text_input("Enter stock ticker (e.g. AAPL or TATAMOTORS):", "AAPL")

if st.button("Analyze"):
    asyncio.run(run_analysis(ticker))

if st.session_state.result:
    # Display Key Metrics
    st.header(f"Key Metrics for {ticker}")
    metrics = get_stock_metrics(ticker)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Price", f"${metrics.get('current_price', 'N/A')}")
        st.metric("P/E Ratio", metrics.get('pe_ratio', 'N/A'))
    with col2:
        market_cap = metrics.get('market_cap')
        display_value = f"${market_cap:,}" if isinstance(market_cap, (int, float)) else str(market_cap)
        st.metric("Market Cap", display_value)
        
        volume = metrics.get('volume')
        display_value = f"{volume:,}" if isinstance(volume, (int, float)) else str(volume)
        st.metric("Volume", display_value)
    with col3:
        low = metrics.get('52_week_low')
        high = metrics.get('52_week_high')
        range_str = f"${low} - ${high}" if isinstance(low, (int, float)) and isinstance(high, (int, float)) else str(low)
        st.metric("52 Week Range", range_str)
        
        avg_vol = metrics.get('avg_volume')
        display_value = f"{avg_vol:,}" if isinstance(avg_vol, (int, float)) else str(avg_vol)
        st.metric("Avg Volume", display_value)

    # Display Recent News
    st.header("Recent News")
    news = get_stock_news(ticker)
    if news.get('news'):
        for item in news['news'][:5]:  # Show top 5 news items
            with st.expander(item['title']):
                st.write(item['description'])
                st.caption(f"Source: {item['url']}")
    else:
        st.warning("No recent news found")

    # Display Agent Debate
    st.header("Agent Discussion")
    for msg in st.session_state.conversation:
        avatar = "🟢" if "Bullish" in msg['role'] else "🔴"
        with st.chat_message(msg['role'], avatar=avatar):
            st.write(msg['content'])

    # Display Recommendation
    st.header("Final Recommendation")
    st.info(st.session_state.result['conclusion'])
