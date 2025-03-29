import asyncio
import json
import logging
from openai import OpenAI
from agents import BullishAssistant, BearishAssistant
import os
from dotenv import load_dotenv
from app_logging import log_agent_call, log_conclusion

load_dotenv()

class StockDebateSystem:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.bullish_agent = BullishAssistant(self.client)
        self.bearish_agent = BearishAssistant(self.client)
    
    async def analyze_stock(self, ticker: str, research_data: dict = None, stream_handler=None):
        """Run stock analysis debate between agents using shared thread"""
        if research_data is None:
            from data_fetcher import get_stock_research
            research_data = get_stock_research(ticker)
        
        # Log agent calls
        log_agent_call("Bullish Agent", ticker)
        log_agent_call("Bearish Agent", ticker)
        
        # Create shared thread
        thread = self.client.beta.threads.create()
        
        # Post research data to thread
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=json.dumps({
                "type": "research_data",
                "ticker": ticker,
                "data": research_data
            })
        )
        
        debate_result = {'messages': [], 'thread_id': thread.id}
        
        try:
            # Conduct 5-round debate alternating between agents
            for turn in range(10):
                is_bullish = turn % 2 == 0
                agent = self.bullish_agent if is_bullish else self.bearish_agent
                
                # Prepare opponent's last message if available
                opponent_last_msg = debate_result['messages'][-1]['content'] if debate_result['messages'] else None
                
                # Get agent's response
                response = await agent.analyze(
                    thread_id=thread.id,
                    research_data=research_data,
                    opponent_last_msg=opponent_last_msg
                )
                
                # Store message
                role = "Bullish Analyst" if is_bullish else "Bearish Analyst"
                debate_result['messages'].append({
                    'role': role,
                    'content': response
                })
        except Exception as e:
            logging.error(f"Debate execution error: {str(e)}")
            debate_result['error'] = str(e)
        
        # Use LLM to generate final conclusion based on debate
        conclusion_prompt = f"""Summarize the following debate about {ticker} stock and provide a final investment recommendation (BUY, SELL, or HOLD) with a brief justification based ONLY on the arguments presented.
        
        Debate Transcript:
        {json.dumps(debate_result['messages'], indent=2)}
        
        Final Recommendation (BUY/SELL/HOLD) and Justification:"""
        
        try:
            conclusion_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a neutral financial analyst summarizing a debate."},
                    {"role": "user", "content": conclusion_prompt}
                ],
                temperature=0.5,
                max_tokens=150
            )
            conclusion = conclusion_response.choices[0].message.content
        except Exception as e:
            logging.error(f"Conclusion generation error: {str(e)}")
            conclusion = "Error generating conclusion."
        
        debate_result['conclusion'] = conclusion
        
        # Clean up thread after completion
        try:
            self.client.beta.threads.delete(thread.id)
        except Exception as e:
            logging.error(f"Error deleting thread {thread.id}: {str(e)}")
            
        return debate_result

if __name__ == "__main__":
    print("This module is meant to be imported, not run directly.")
