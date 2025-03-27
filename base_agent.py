from custom_agent import Agent
import os

class StockAgent(Agent):
    def __init__(self, name: str, persona: str, system_prompt: str):
        super().__init__(
            name=name,
            persona=persona,
            system_prompt=system_prompt
        )
        self.api_key = os.getenv("OPENAI_API_KEY")
