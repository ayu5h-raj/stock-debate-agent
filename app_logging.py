import logging
from datetime import datetime
import os

def setup_logging():
    """Configure logging for the application"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler()
        ]
    )

def log_conversation(agent_name: str, content: str, ticker: str):
    """Log agent conversations with timestamp"""
    logging.info(f"[{ticker}] {agent_name}: {content}")

def log_agent_call(agent_name: str, ticker: str):
    """Log when an agent is called"""
    logging.info(f"{agent_name} analyzing {ticker}")

def log_tool_use(tool_name: str, params: dict):
    """Log when a research tool is used"""
    logging.info(f"Tool used: {tool_name} with params: {params}")

def log_conclusion(ticker: str, conclusion: str):
    """Log the final recommendation"""
    logging.info(f"Final recommendation for {ticker}: {conclusion}")

def format_conversation_log(messages: list) -> str:
    """Format complete conversation for logging"""
    return "\n".join(
        f"[{msg['role']}] {msg['content']}" 
        for msg in messages
    )
