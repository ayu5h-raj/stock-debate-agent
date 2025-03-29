# Stock Analysis AI Debate Agent

This project implements a Stock Analysis system using two AI agents, representing Bullish and Bearish perspectives, who engage in a debate to analyze a given stock ticker. The system leverages the OpenAI Chat Completions API with streaming for the debate and final conclusion, fetches real-time financial metrics and news, and presents the analysis through a Streamlit web interface.

## Features

*   **AI-Powered Debate:** Employs two specialized AI agents (Bullish and Bearish) powered by `gpt-4o-mini` via the OpenAI Chat Completions API.
*   **Streaming Responses:** The debate between the agents is displayed in real-time using streaming responses.
*   **Symbol Lookup:** Can find the correct stock ticker symbol from a company name using an LLM call.
*   **Real-time Data Fetching:** Integrates with Yahoo Finance (via `yfinance`) for financial metrics and Tavily API for the latest news headlines.
*   **Key Metrics Display:** Shows important metrics (Price, Market Cap, P/E) upfront before the detailed analysis begins.
*   **Structured Analysis:** Provides a final investment conclusion (e.g., Buy, Sell, Hold) based on the debate and fetched data.
*   **Interactive UI:** Built with Streamlit for easy interaction, allowing users to input tickers/company names and view the analysis, debate, and fetched data.
*   **API Key Management:** Securely handles API keys using Streamlit secrets or a local `.env` file.

## Architecture

The system consists of the following main components:

1.  **Streamlit App (`app.py`):** Handles user input (ticker/company name), manages API keys, orchestrates the analysis flow, and displays results.
2.  **Debate System (`main.py`):** The `StockDebateSystem` class manages the interaction between the agents. It fetches necessary data, facilitates the debate rounds using streaming, and generates a final conclusion using the Chat Completions API.
3.  **Chat Agents (`agents.py`):** Defines the `BullishChatAgent` and `BearishChatAgent` classes. These agents use the OpenAI Chat Completions API to generate their arguments based on system prompts, conversation history, and provided research data (metrics & news summary).
4.  **Data Fetcher (`data_fetcher.py`):** Contains functions to:
    *   Fetch financial metrics using `yfinance` (`get_stock_metrics`).
    *   Fetch news headlines using the Tavily API (`get_stock_news`).
    *   Find a stock symbol for a given company name using an OpenAI API call (`get_stock_symbol`).

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ayu5h-raj/stock-debate-agent.git
    cd stock-debate-agent
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate 
    # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Keys:**
    *   **Option 1 (Recommended): `.env` file:**
        Create a file named `.env` in the project root directory and add your API keys:
        ```
        OPENAI_API_KEY="your_openai_api_key"
        TAVILY_API_KEY="your_tavily_api_key"
        ```
    *   **Option 2: Streamlit Secrets (for deployment):**
        If deploying via Streamlit Community Cloud, configure secrets according to their documentation.
    *   **Option 3: Manual Input:**
        Run the app and enter the keys via the Streamlit sidebar (keys are not persistently stored).

## Usage

1.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

2.  **Enter API Keys:** If not using `.env` or secrets, provide your OpenAI and Tavily API keys in the sidebar.

3.  **Enter Stock Ticker or Company Name:** Input the stock ticker (e.g., `AAPL`) or the company name (e.g., `Apple Inc.`) in the main input field.
    *   If a company name is entered, the app will attempt to find the corresponding ticker.
    *   If multiple potential symbols are found, you will be prompted to select the correct one in the sidebar.

4.  **Click "Analyze [Symbol/Company]":** The analysis will begin.
    *   Key metrics will be displayed first.
    *   The debate between the Bullish and Bearish agents will stream in the main area.
    *   A final conclusion will be generated and displayed.
    *   An expander section allows viewing the raw financial metrics and news data fetched.

## Application Flow

Stock Analysis Flow:

```
[User Input]
   |
   v
[Streamlit UI] 
   |
   v
[StockDebateSystem]
   /       \
  v         v
[BullishAgent] [BearishAgent]
  |             |
  v             v
[OpenAI API] [OpenAI API]
  |             |
  v             v
[Debate Engine]
   |
   v
[Conclusion Generator]
   |
   v
[Results Display]
```

Simplified Flow Overview:

```
[User Input]
   |
   v
[Streamlit UI] 
   |
   v
[StockDebateSystem]
   /       \
  v         v
[BullishAgent] [BearishAgent]
  |             |
  v             v
[OpenAI API] [OpenAI API]
  |             |
  v             v
[Debate Engine]
   |
   v
[Conclusion Generator]
   |
   v
[Results Display]
```

## Code Structure

```
stock-debate-agent/
├── .env.example         # Example environment file
├── .gitignore
├── README.md            # This file
├── agents.py            # Defines Bullish and Bearish Chat Agents
├── app.py               # Main Streamlit application
├── data_fetcher.py      # Functions for fetching stock data and news
├── main.py              # Core StockDebateSystem logic
├── requirements.txt     # Python dependencies
└── venv/                # Virtual environment directory (if created)
```

## Future Enhancements

*   More sophisticated data fetching (e.g., analyst ratings, insider trading).
*   Advanced agent reasoning and memory.
*   Visualization of financial data.
*   Allowing user interaction during the debate.
