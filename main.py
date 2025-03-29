import streamlit as st
import asyncio
from openai import AsyncOpenAI 
from agents import BullishChatAgent, BearishChatAgent 
from data_fetcher import get_stock_metrics, get_stock_news
from typing import List, Dict, Optional
import json
import traceback 

class StockDebateSystem:
    def __init__(self, openai_api_key: str, tavily_api_key: str):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.bull_agent = BullishChatAgent(self.client)
        self.bear_agent = BearishChatAgent(self.client)
        self.debate_rounds = 2 
        self.tavily_api_key = tavily_api_key

    def _add_message(self, role: str, content: str, history: List[Dict[str, str]]) -> None:
        history.append({"role": role, "content": content})

    async def analyze_stock(self, ticker: str, initial_metrics: Optional[dict] = None, stream_handler=None) -> tuple:
        research_data = {}
        metrics = initial_metrics # Use pre-fetched metrics if available
        news = None

        if not metrics:
            st.write(f"Fetching metrics data for {ticker}...")
            metrics = get_stock_metrics(ticker)
        research_data['metrics'] = metrics

        if not metrics or metrics.get('error'):
            error_msg = metrics.get('error', f"Could not fetch metrics data for {ticker}.")
            st.error(error_msg)
            # Return metrics even if error, so UI can show partial data
            return error_msg, research_data 

        # Fetch news separately (can still be done asynchronously later if needed)
        st.write(f"Fetching news data for {ticker}...")
        news = get_stock_news(ticker)
        research_data['news'] = news 
        if news.get('error'):
             st.warning(f"Could not fetch news: {news['error']}") # Warning instead of error

        # --- Combine metrics and news for the agents --- 
        # Prepare a combined dictionary or string representation for the agents
        # Example: Create a summary string (adjust formatting as needed)
        combined_research = f"Stock: {ticker}\n\nMetrics:\n"
        if isinstance(metrics, dict):
            for key, value in metrics.items():
                 if key != 'error': # Don't include error key in agent data
                    combined_research += f"- {key.replace('_', ' ').title()}: {value}\n"
        else:
            combined_research += "- Metrics N/A\n"
        
        combined_research += "\nNews Headlines:\n"
        if isinstance(news, dict) and 'news' in news:
            headlines = [item.get('title', 'N/A') for item in news['news']]
            if headlines:
                combined_research += "- " + "\n- ".join(headlines)
            else:
                combined_research += "- No recent news found."
        else:
            combined_research += "- News N/A"

        # Start debate logic using combined_research
        conversation_history: List[Dict[str, str]] = [] 
        
        last_message = None
        current_agent = self.bull_agent

        try:
            for round_num in range(self.debate_rounds * 2): 
                agent_name = "Bullish Analyst" if current_agent == self.bull_agent else "Bearish Analyst"
                st.write(f"\n--- Round {round_num // 2 + 1} ({agent_name}) ---")

                round_research_data = combined_research 

                full_response = ""
                placeholder = st.empty()
                stream_content = ""
                
                async for chunk in current_agent.generate_response_stream(
                    conversation_history=conversation_history,
                    research_data_str=round_research_data, # Pass combined string
                    opponent_last_msg=last_message 
                ):
                    stream_content += chunk
                    placeholder.markdown(stream_content + "▌") 
                
                placeholder.markdown(stream_content) 
                full_response = stream_content
                last_message = full_response 

                self._add_message("assistant", full_response, conversation_history)
                
                current_agent = self.bear_agent if current_agent == self.bull_agent else self.bull_agent
            
            st.write("\n--- Generating Final Conclusion ---")
            
            conclusion_prompt = "Based on the preceding debate between a bullish and bearish analyst regarding {}, using the provided context (metrics and news headlines), provide a concise final investment conclusion (e.g., Strong Buy, Buy, Hold, Sell, Strong Sell) and a brief (1-2 sentence) justification. Consider the strengths of both arguments.".format(ticker)
            self._add_message("user", conclusion_prompt, conversation_history)

            # Prepend combined research to the history for final conclusion context
            final_messages = [
                {"role": "system", "content": "You are a neutral financial analyst synthesizing a debate to provide a final investment conclusion."}, 
                {"role": "user", "content": f"Context:\n{combined_research}\n\nDebate History:"} # Add context here
            ] + conversation_history

            final_response = await self.client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=final_messages, # Use messages with prepended context
                temperature=0.5, 
                max_tokens=150
            )
            
            st.write(final_response.choices[0].message.content)
            self._add_message("assistant", final_response.choices[0].message.content, conversation_history)
            
            # Return the raw research_data dictionary for the UI expander
            return final_response.choices[0].message.content, research_data 
        
        except Exception as e:
            st.error(f"An error occurred during the debate: {e}")
            print(traceback.format_exc()) 
            return f"Debate failed due to an error: {e}", research_data
