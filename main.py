import asyncio
from agents import BullishAgent, BearishAgent
from custom_agent import AgentSystem
import os
from dotenv import load_dotenv

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
        
        # Run parallel research
        await asyncio.gather(
            self.bullish_agent.research(ticker, research_prompt),
            self.bearish_agent.research(ticker, research_prompt)
        )
        
        # Conduct debate
        debate_result = await self.system.run_debate(
            agents=[self.bullish_agent, self.bearish_agent],
            turns=5,
            topic=f"Should we buy {ticker} stock?",
            stream_handler=stream_handler
        )
        
        return debate_result

if __name__ == "__main__":
    print("This module is meant to be imported, not run directly.")
