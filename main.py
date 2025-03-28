import asyncio
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
    
    async def analyze_stock(self, ticker: str, stream_handler=None):
        """Run stock analysis debate between agents"""
        research_prompt = f"Research the stock {ticker} and prepare arguments"
        
        # Fetch research data once and share between agents
        from data_fetcher import get_stock_research
        research_data = get_stock_research(ticker)
        
        # Have agents analyze the same data from different perspectives
        log_agent_call("Bullish Agent", ticker)
        log_agent_call("Bearish Agent", ticker)
        await asyncio.gather(
            self.bullish_agent.analyze(research_data, research_prompt),
            self.bearish_agent.analyze(research_data, research_prompt)
        )
        
        # Conduct debate
        debate_result = await self.system.run_debate(
            agents=[self.bullish_agent, self.bearish_agent],
            turns=5,
            topic=f"Should we buy {ticker} stock?",
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
