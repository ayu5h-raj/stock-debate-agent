# Stock Analysis AI Agent System

![Stock Analysis Demo](https://example.com/stock-analysis-demo.gif) *[Demo screenshot placeholder]*

## Overview

A sophisticated AI system that employs two autonomous agents (bullish and bearish) to analyze stocks through reasoned debate. The agents research financial data, discuss their perspectives, and provide a balanced investment recommendation.

## Key Features

- 🤖 **Dual-Agent Architecture**: Bullish and bearish agents provide balanced analysis
- 📊 **Multi-Source Data**: Integrates real-time data from:
  - yfinance for financial metrics
  - Tavily API for news and executive changes
- 🌐 **Global Stock Support**: Handles both US and international markets
- 📈 **Comprehensive Analysis**: Evaluates:
  - Financial metrics (P/E, market cap, volume)
  - Recent news developments
  - Executive changes
- 💬 **Interactive Debate**: Watch AI agents discuss investment merits
- 📱 **Streamlit UI**: Clean, intuitive interface for easy interaction

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/stock-agent.git
cd stock-agent
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Get API keys:
   - [OpenAI API Key](https://platform.openai.com/api-keys)
   - [Tavily API Key](https://tavily.com/)

2. Provide API keys:
   - Either through the Streamlit UI when running the app
   - Or by creating a `.env` file:
```ini
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Input requirements:
   - Enter your API keys in the sidebar
   - Provide a stock ticker or company name (e.g. "AAPL" or "Apple")  
   - Click "Analyze"

3. View results:
   - Key financial metrics
   - Recent news items
   - Agent discussion transcript
   - Final investment recommendation

## Technology Stack

- **Core**: Python 3.10+
- **AI Framework**: OpenAI Agents SDK
- **Natural Language**: GPT models via OpenAI API
- **Data Sources**:
  - yfinance for market data
  - Tavily for web search/news
- **UI**: Streamlit
- **Async Processing**: asyncio
- **Environment Management**: python-dotenv

## Code Structure

```
stock-agent/
├── app.py                # Streamlit UI and main application
├── agents.py             # Bullish/Bearish agent implementations  
├── base_agent.py         # Base agent class
├── custom_agent.py       # Custom agent system extensions
├── data_fetcher.py       # Financial data retrieval
├── main.py               # Core debate system
├── app_logging.py        # Logging utilities
├── README.md             # This documentation
└── requirements.txt      # Dependencies
```

## Example Analysis

Here's sample output for analyzing Apple (AAPL):

**Key Metrics**:
- Current Price: $189.56
- P/E Ratio: 29.34  
- Market Cap: $2.91T
- 52 Week Range: $143.90 - $198.23

**Recent News**:
- Apple announces new AI features in iOS 18
- Morgan Stanley raises price target to $220
- Supply chain issues reported in China factories

**Agent Discussion**:
🟢 **Bullish Agent**: "Apple's ecosystem strength justifies premium valuation"
🔴 **Bearish Agent**: "Supply chain risks may impact holiday quarter"

**Final Recommendation**: BUY - Strong fundamentals outweigh short-term risks

## Limitations

1. Not financial advice - for educational purposes only
2. API costs may apply for extensive usage
3. Limited to publicly available information

