from base_agent import StockAgent
import requests
from typing import Optional
import os

class BullishAgent(StockAgent):
    def __init__(self):
        super().__init__(
            name="Bullish Analyst",
            persona="You are an optimistic but conversational stock analyst. "
                   "You focus on positive trends, strong fundamentals, and future opportunities. "
                   "Respond in clear, concise paragraphs with natural breaks between thoughts.",
            system_prompt="Analyze stocks conversationally with a bullish perspective. "
                        "Highlight 2-3 key growth factors per response. "
                        "Keep responses under 3 sentences. "
                        "Use natural language as if explaining to a colleague."
        )
        
    async def analyze(self, research_data: str, prompt: str) -> str:
        """Analyze stock research data from bullish perspective"""
        return await self.generate_response(
            prompt=f"{prompt}\nAnalyze this stock with a bullish perspective:\n{research_data}",
            max_tokens=1000
        )

class BearishAgent(StockAgent):
    def __init__(self):
        super().__init__(
            name="Bearish Analyst",
            persona="You are a cautious but conversational stock analyst. "
                   "You identify risks and downsides in a clear, measured way. "
                   "Respond in digestible chunks with natural pauses.",
            system_prompt="Analyze stocks conversationally with a bearish perspective. "
                        "Highlight 2-3 key risks per response. "
                        "Keep responses under 3 sentences. "
                        "Use natural language as if warning a colleague."
        )
        
    async def analyze(self, research_data: str, prompt: str) -> str:
        """Analyze stock research data from bearish perspective"""
        return await self.generate_response(
            prompt=f"{prompt}\nAnalyze this stock with a bearish perspective:\n{research_data}",
            max_tokens=1000
        )
