import streamlit as st
from main import StockDebateSystem
import asyncio

st.set_page_config(page_title="Stock Debate AI", layout="wide")

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'result' not in st.session_state:
    st.session_state.result = None

async def handle_stream(agent_name: str, content: str):
    """Handle streaming response chunks with full message history"""
    # Initialize message tracking
    if 'message_history' not in st.session_state:
        st.session_state.message_history = []
        st.session_state.current_message = None
    
    # Start new message if needed
    if st.session_state.current_message is None or st.session_state.current_message["role"] != agent_name:
        st.session_state.current_message = {
            "role": agent_name,
            "content": "",
            "container": None
        }
        st.session_state.message_history.append(st.session_state.current_message)
    
    # Append new content
    st.session_state.current_message["content"] += content
    
    # Create container if it doesn't exist
    if st.session_state.current_message["container"] is None:
        st.session_state.current_message["container"] = st.empty()
    
    # Update display
    with st.session_state.current_message["container"]:
        with st.chat_message(agent_name, avatar="🟢" if "Bullish" in agent_name else "🔴"):
            st.markdown(st.session_state.current_message["content"])

async def run_analysis(ticker):
    """Run stock analysis and update UI with streaming"""
    if not ticker or len(ticker.strip()) == 0:
        st.error("Please enter a stock ticker")
        return None
        
    ticker = ticker.strip().upper()
    system = StockDebateSystem()
    
    # Clear previous state
    st.session_state.conversation = []
    st.session_state.result = None
    
    with st.spinner(f"Analyzing {ticker}..."):
        result = await system.analyze_stock(ticker, stream_handler=handle_stream)
        st.session_state.result = result
        st.session_state.conversation.extend(result['messages'])
    return result

def export_conversation():
    """Export conversation to a text file"""
    if not st.session_state.result:
        return
    
    content = f"Stock Analysis for {ticker}\n\n"
    content += f"Conclusion: {st.session_state.result['conclusion']}\n\n"
    content += "Debate Transcript:\n"
    for msg in st.session_state.conversation:
        content += f"{msg['role']}: {msg['content']}\n\n"
    
    return content

# UI Layout
st.title("Stock Analysis AI Debate")
ticker = st.text_input("Enter stock ticker:", "AAPL")

if st.button("Analyze"):
    asyncio.run(run_analysis(ticker))

if st.session_state.result:
    st.header(f"Analysis for {ticker}")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Final Conclusion")
        st.write(st.session_state.result.get('conclusion', 'No conclusion generated.'))
    with col2:
        st.download_button(
            label="Export Conversation",
            data=export_conversation(),
            file_name=f"stock_debate_{ticker}.txt",
            mime="text/plain"
        )

    st.subheader("Debate Summary")
    st.write(st.session_state.result['summary'])

    st.subheader("Debate Transcript")
    for msg in st.session_state.conversation:
        avatar = "🟢" if "Bullish" in msg['role'] else "🔴"
        with st.chat_message(msg['role'], avatar=avatar):
            st.write(msg['content'])

# Sidebar with info
with st.sidebar:
    st.header("About")
    st.write("""
    This app uses two AI agents with opposing views to analyze stocks.
    The Bullish Agent looks for growth potential while the Bearish Agent
    identifies risks. Their debate provides balanced insights.
    """)
    st.warning("Note: This is not financial advice. Do your own research.")
