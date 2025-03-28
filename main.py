import asyncio
import json
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
        """Run stock analysis debate between assistants using Threads"""
        if research_data is None:
            from data_fetcher import get_stock_research
            research_data = get_stock_research(ticker)
        
        # Create thread for this analysis
        thread = self.client.beta.threads.create()
        
        # Initialize debate
        debate_result = {'messages': []}
        debate_topic = f"Analyze {ticker} stock. Here's the research data: {json.dumps(research_data)}"
        
        # Alternate between agents for 5 turns
        for turn in range(5):
            agent = self.bullish_agent if turn % 2 == 0 else self.bearish_agent
            response = await agent.analyze(thread.id, research_data)
            
            # Store message in debate result
            role = "Bullish Analyst" if turn % 2 == 0 else "Bearish Analyst"
            debate_result['messages'].append({
                'role': role,
                'content': response
            })
        
        # Analyze debate and generate recommendation
        buy_weight = 0
        sell_weight = 0
        bullish_points = []
        bearish_points = []
        
        for msg in debate_result['messages']:
            content = msg['content']
            if "bullish" in msg['role'].lower():
                buy_weight += 1
                bullish_points.append("- " + content.split('.')[0] + ".")
            elif "bearish" in msg['role'].lower():
                sell_weight += 1  
                bearish_points.append("- " + content.split('.')[0] + ".")
        
        confidence = abs(buy_weight - sell_weight)/max(len(debate_result['messages']),1)
        
        conclusion = f"After analyzing {ticker}, our recommendation is to "
        if buy_weight > sell_weight and confidence > 0.25:
            conclusion += f"BUY with {int(confidence*100)}% confidence.\n\n"
            conclusion += "Key bullish points:\n" + "\n".join(bullish_points[-3:])
        elif sell_weight > buy_weight and confidence > 0.25:
            conclusion += f"SELL with {int(confidence*100)}% confidence.\n\n"
            conclusion += "Key bearish points:\n" + "\n".join(bearish_points[-3:])
        else:
            conclusion += "HOLD as arguments are balanced.\n\n"
            conclusion += "Bullish considerations:\n" + "\n".join(bullish_points[:3])
            conclusion += "\n\nBearish considerations:\n" + "\n".join(bearish_points[:3])
        
        debate_result['conclusion'] = conclusion
        return debate_result

if __name__ == "__main__":
    print("This module is meant to be imported, not run directly.")
