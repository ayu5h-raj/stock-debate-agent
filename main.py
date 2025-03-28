import asyncio
import json
from agents import BullishAgent, BearishAgent
from custom_agent import AgentSystem
import os
from dotenv import load_dotenv
from app_logging import log_agent_call, log_conclusion

load_dotenv()

class StockDebateSystem:
    def __init__(self):
        self.system = AgentSystem()
        self.bullish_agent = BullishAgent()
        self.bearish_agent = BearishAgent()
        
        self.system.register_agent(self.bullish_agent)
        self.system.register_agent(self.bearish_agent)
    
    async def analyze_stock(self, ticker: str, research_data: dict = None, stream_handler=None):
        """Run stock analysis debate between agents using provided research data"""
        if research_data is None:
            from data_fetcher import get_stock_research
            research_data = get_stock_research(ticker)
        
        # Log agent calls
        log_agent_call("Bullish Agent", ticker)
        log_agent_call("Bearish Agent", ticker)
        
        # Conduct debate, passing research data as context
        debate_topic = f"Should we buy {ticker} stock? Consider these key metrics and recent news."
        # Format context nicely for the LLM
        context_str = f"--- Start Context for {ticker} ---\n"
        context_str += f"Metrics: {json.dumps(research_data.get('metrics', {}), indent=2)}\n\n"
        context_str += f"News: {json.dumps(research_data.get('news', {}).get('news', []), indent=2)}\n\n"
        context_str += f"--- End Context for {ticker} ---"

        debate_result = await self.system.run_debate(
            agents=[self.bullish_agent, self.bearish_agent],
            turns=5,
            topic=debate_topic,
            context=context_str,
            stream_handler=stream_handler
        )
        
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
