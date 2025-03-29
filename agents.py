from openai import OpenAI
from typing import Optional
import os
import json

class StockAssistant:
    def __init__(self, client: OpenAI, name: str, instructions: str):
        self.client = client
        self.name = name
        self.assistant = self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=[{"type": "function", "function": {
                "name": "get_stock_research",
                "description": "Get research data for a stock",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["ticker"]
                }
            }}],
            model="gpt-4-1106-preview"
        )

    async def analyze(self, thread_id: str, research_data: dict) -> str:
        """Run analysis using Assistant API with thread"""
        try:
            # Add research data to thread
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=json.dumps(research_data)
            )

            # Run assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant.id
            )

            # Wait for completion
            while run.status != "completed":
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

            # Get response
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            return messages.data[0].content[0].text.value

        except Exception as e:
            print(f"Error in {self.name} analysis: {str(e)}")
            return ""

class BullishAssistant(StockAssistant):
    def __init__(self, client: OpenAI):
        instructions = """You are a bullish stock analyst. Focus on:
- Growth potential and opportunities
- Positive trends and catalysts
- Strong fundamentals
Keep responses concise (2-3 sentences) and conversational."""
        super().__init__(client, "Bullish Analyst", instructions)

class BearishAssistant(StockAssistant):
    def __init__(self, client: OpenAI):
        instructions = """You are a bearish stock analyst. Focus on:
- Risks and challenges
- Negative indicators
- Competitive threats
Keep responses concise (2-3 sentences) and measured."""
        super().__init__(client, "Bearish Analyst", instructions)
