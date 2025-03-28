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
        context_str += f"Executive Changes: {json.dumps(research_data.get('executives', {}).get('executive_changes', []), indent=2)}\n"
        context_str += f"--- End Context for {ticker} ---"

        debate_result = await self.system.run_debate(
            agents=[self.bullish_agent, self.bearish_agent],
            turns=5,
            topic=debate_topic,
            context=context_str, # Pass formatted context
            stream_handler=stream_handler
        )
        
        # Generate concise conclusion
        conclusion = f"After analyzing {ticker}, our recommendation is to "
        if len(debate_result['messages']) > 0:
            last_message = debate_result['messages'][-1]['content']
            if "buy" in last_message.lower():
                conclusion += "BUY. The growth potential outweighs the risks."
            elif "sell" in last_message.lower():
                conclusion += "SELL. The risks outweigh the potential gains."
            else:
                conclusion += "HOLD. The risks and potential are balanced."
        
        debate_result['conclusion'] = conclusion
        return debate_result

if __name__ == "__main__":
    print("This module is meant to be imported, not run directly.")
