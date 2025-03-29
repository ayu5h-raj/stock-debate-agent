import streamlit as st
import os
import threading # Import threading
from dotenv import load_dotenv
from main import StockDebateSystem
import traceback # Import traceback for error logging
from streamlit.errors import StreamlitAPIException # For catching secrets error
# Import the function to find symbols
from data_fetcher import get_stock_symbol 
from data_fetcher import get_stock_metrics # Import metrics function
import asyncio # Import asyncio

# Load environment variables FIRST. This loads from .env into os.environ
load_dotenv()

# --- Page Configuration ---
st.set_page_config(page_title="Stock Analyst Debate", layout="wide")
st.title("Stock Analyst AI Debate System 📈 vs 📉")

# --- API Key Management --- 
st.sidebar.header("API Configuration")

# 1. Get values from sidebar inputs 
openai_api_key_input = st.sidebar.text_input(
    "OpenAI API Key", 
    value="",  # Start empty
    type="password",
    help="Enter key to override .env/secrets, or leave blank."
)
tavily_api_key_input = st.sidebar.text_input(
    "Tavily API Key", 
    value="",  # Start empty
    type="password",
    help="Enter key to override .env/secrets, or leave blank."
)

# 2. Determine final keys with priority: Input > .env > secrets
openai_api_key = openai_api_key_input
tavily_api_key = tavily_api_key_input
source_feedback = {"openai": "Input", "tavily": "Input"}

# Check .env (os.environ) if input is empty
if not openai_api_key:
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if openai_api_key:
        source_feedback["openai"] = ".env File"

if not tavily_api_key:
    tavily_api_key = os.getenv("TAVILY_API_KEY", "")
    if tavily_api_key:
        source_feedback["tavily"] = ".env File"

# Check secrets only if still empty (and secrets are available)
secrets_available = False
try:
    if hasattr(st, 'secrets') and st.secrets and len(st.secrets) > 0:
         secrets_available = True
except (AttributeError, StreamlitAPIException):
    secrets_available = False

if secrets_available:
    if not openai_api_key: 
        openai_api_key = st.secrets.get("OPENAI_API_KEY", "")
        if openai_api_key:
            source_feedback["openai"] = "Secrets"
            
    if not tavily_api_key: 
        tavily_api_key = st.secrets.get("TAVILY_API_KEY", "")
        if tavily_api_key:
            source_feedback["tavily"] = "Secrets"

# Display feedback on key source
st.sidebar.caption(f"OpenAI Key Source: {source_feedback['openai']}")
st.sidebar.caption(f"Tavily Key Source: {source_feedback['tavily']}")

if source_feedback["openai"] == "Input" or source_feedback["tavily"] == "Input":
    st.sidebar.info("Keys entered in sidebar override .env/secrets for this session.")
elif source_feedback["openai"] == ".env File" or source_feedback["tavily"] == ".env File":
     st.sidebar.info("Using keys found in local .env file.")
elif source_feedback["openai"] == "Secrets" or source_feedback["tavily"] == "Secrets":
     st.sidebar.info("Using keys from Streamlit secrets.")


# --- System Initialization --- 
debate_system = None # Default to None

if openai_api_key and tavily_api_key:
    current_keys_tuple = (openai_api_key, tavily_api_key)

    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False
        st.session_state.debate_system = None
        st.session_state.last_keys_used = None

    if not st.session_state.system_initialized or \
       st.session_state.last_keys_used != current_keys_tuple:

        st.session_state.system_initialized = False 
        st.session_state.debate_system = None

        with st.sidebar:
            with st.spinner("Initializing Debate System..."):
                try:
                    st.session_state.debate_system = StockDebateSystem(
                        openai_api_key=openai_api_key,
                        tavily_api_key=tavily_api_key
                    )
                    st.session_state.system_initialized = True
                    st.session_state.last_keys_used = current_keys_tuple
                    st.success("System Initialized!") 
                except Exception as e:
                    st.error(f"Initialization failed: {e}")
                    st.session_state.system_initialized = False

    if st.session_state.get('system_initialized'):
        debate_system = st.session_state.get('debate_system') 

if not debate_system:
    st.warning("System not initialized. Please provide valid API keys (Checked: Input > .env > Secrets).")
    st.stop()

# --- UI Elements --- 
st.sidebar.header("Stock Analysis")

# Input for Company Name or Symbol
company_input = st.sidebar.text_input(
    "Enter Company Name or Ticker Symbol (e.g., Apple, NVDA, Reliance Industries)", 
    value="Nvidia" # Default example
)
find_symbol_button = st.sidebar.button("Find Symbol / Verify")

# Initialize session state for symbols and selected symbol
if 'found_symbols' not in st.session_state:
    st.session_state.found_symbols = None
if 'selected_symbol' not in st.session_state:
    st.session_state.selected_symbol = None

# --- Symbol Lookup Logic --- 
if find_symbol_button:
    st.session_state.found_symbols = None # Reset on new search
    st.session_state.selected_symbol = None
    symbol = None 
    error_message = None

    if not company_input:
        st.sidebar.warning("Please enter a company name or symbol.")
    elif not debate_system: # Need system initialized for Tavily key
         st.sidebar.error("System not initialized. Check API keys.")
    else:
        with st.sidebar:
            with st.spinner(f"Searching symbols for '{company_input}'..."):
                # Define a target function for the thread
                def find_symbol_thread():
                    global symbol, error_message 
                    try:
                        # Call the synchronous function
                        found_symbol = get_stock_symbol(company_input) 
                        if found_symbol:
                            symbol = found_symbol
                        else:
                            error_message = f"Could not find a valid symbol for '{company_input}'."
                    except Exception as thread_e:
                         error_message = f"Error during symbol search thread: {thread_e}"
                
                # Create and start the thread
                thread = threading.Thread(target=find_symbol_thread)
                thread.start()
                thread.join() # Wait for the thread to finish

                # Process results after thread completes
                if symbol:
                    st.session_state.found_symbols = [{'symbol': symbol, 'name': company_input}] # Store as list for consistency
                    st.session_state.selected_symbol = symbol
                    st.success(f"Verified Symbol: {st.session_state.selected_symbol}")
                elif error_message:
                    st.error(error_message)
                    st.session_state.found_symbols = [] # Indicate error
                else: # Should not happen if logic above is correct, but handle defensively
                    st.error("An unknown issue occurred during symbol lookup.")
                    st.session_state.found_symbols = []

# --- Symbol Selection --- 
# Check if found_symbols is a list (covers successful search and failed search cases)
if isinstance(st.session_state.found_symbols, list): 
    if len(st.session_state.found_symbols) > 1:
         # Format options for selectbox: "Symbol (Name)"
         symbol_options = {f"{s['symbol']} ({s.get('name', 'N/A')})": s['symbol'] 
                           for s in st.session_state.found_symbols}
         
         selected_display = st.sidebar.selectbox(
             "Select the correct stock symbol:",
             options=symbol_options.keys(), 
             index=0 # Default to first option
         )
         # Update selected_symbol based on selection
         st.session_state.selected_symbol = symbol_options[selected_display]
         st.sidebar.write(f"Selected: **{st.session_state.selected_symbol}**")
    
    # Handle case where search was attempted but nothing found
    elif len(st.session_state.found_symbols) == 0 and find_symbol_button:
        st.sidebar.warning("No symbols found from the search.")

# --- Analysis Execution Trigger --- 
# Only show analyze button if a symbol is selected/verified
analyze_button = None 
ticker = None # Define ticker variable outside the if block
if st.session_state.selected_symbol:
    ticker = st.session_state.selected_symbol # Assign selected symbol to ticker
    analyze_button = st.sidebar.button(f"Analyze {ticker}")
else:
    st.sidebar.caption("Find/verify a symbol to enable analysis.")


# --- Main Display Area --- 
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("#### Analysis & Debate")
    metrics_container = st.container() # Container for early metrics
    status_container = st.container()
    data_container = st.container() 
    debate_container = st.container() 
    conclusion_container = st.container()

# --- Analysis Execution Logic --- 
# Use the 'analyze_button' state and the 'ticker' variable set above
if analyze_button and ticker: # Check both button press and ticker availability
    # Check system readiness again
    if not debate_system:
         status_container.error("System not initialized. Check API keys.")
    else:
        # Clear previous outputs
        data_container.empty()
        debate_container.empty()
        conclusion_container.empty()
        status_container.empty()
        metrics_container.empty() # Clear metrics container

        with status_container:
             st.info(f"Fetching initial data for {ticker}...")

        # Fetch metrics first
        initial_metrics = get_stock_metrics(ticker)

        if initial_metrics.get('error'):
            status_container.error(f"Failed to fetch initial metrics: {initial_metrics['error']}")
        else:
            # Display key metrics at the top
            with metrics_container:
                st.subheader(f"Key Metrics for {ticker}")
                price = initial_metrics.get('current_price', 'N/A')
                mcap = initial_metrics.get('market_cap', 'N/A')
                pe = initial_metrics.get('pe_ratio', 'N/A')
                currency = initial_metrics.get('currency', '')

                # Format Market Cap nicely
                if isinstance(mcap, (int, float)):
                    if mcap >= 1e12:
                        mcap_display = f"{mcap / 1e12:.2f} T {currency}"
                    elif mcap >= 1e9:
                        mcap_display = f"{mcap / 1e9:.2f} B {currency}"
                    elif mcap >= 1e6:
                         mcap_display = f"{mcap / 1e6:.2f} M {currency}"
                    else:
                        mcap_display = f"{mcap} {currency}"
                else:
                    mcap_display = mcap

                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Current Price", f"{price} {currency}")
                col_m2.metric("Market Cap", mcap_display)
                col_m3.metric("P/E Ratio", f"{pe}")
                st.markdown("---") # Separator

            with status_container:
                 st.info(f"Starting analysis for {ticker}...")
                 st.write("_(Agents are preparing for the debate...)_")

            try:
                # Pass fetched metrics to analyze_stock to avoid re-fetching 
                final_conclusion, fetched_data = asyncio.run(debate_system.analyze_stock(ticker=ticker, initial_metrics=initial_metrics)) 

                # Display full fetched data later in expander (avoid duplication)
                with data_container:
                    with st.expander("View Fetched Research Data"):
                        if fetched_data:
                            st.subheader("Financial Metrics")
                            # Filter out metrics already shown at top if needed, or just show all
                            # Example: Show all fetched metrics for completeness
                            st.json(fetched_data.get('metrics', {}), expanded=False)

                            st.subheader("News & Events")
                            # Check if news data and the 'news' list exist before accessing
                            news_data = fetched_data.get('news', {})
                            news_list = news_data.get('news', []) if isinstance(news_data, dict) else []
                            news_content = "\n".join([f"- {n.get('title', 'N/A')}: {n.get('description', 'N/A')}" for n in news_list]) if news_list else "No news found."
                            st.text_area("News Details", news_content, height=150)

                            # Executive changes might not be fetched in this flow anymore, adjust if needed
                            # st.subheader("Executive Changes")
                            # st.text_area("", fetched_data.get('Executive Changes', "No changes found."), height=100)
                        else:
                            st.write("No full research data was returned.")
            
                # Update status
                status_container.empty() 
                status_container.success(f"Analysis for {ticker} complete.")

                # Display conclusion
                with conclusion_container:
                    st.markdown("--- ")
                    st.markdown("#### Final Conclusion")
                    if isinstance(final_conclusion, str):
                        st.markdown(final_conclusion)
                    else:
                        st.error("Analysis finished, but the final result format was unexpected.")
            
            except Exception as e: 
                status_container.error(f"An application error occurred during analysis: {e}")
                with debate_container:
                     st.error("Traceback:")
                     st.code(traceback.format_exc())

# --- Initial Placeholder --- 
if not analyze_button and 'debate_container' in locals():
     with debate_container:
        # Adjust initial message
        st.markdown("Enter a company name or symbol, click 'Find Symbol / Verify', select the symbol (if needed), and then click 'Analyze'.")
