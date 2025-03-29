from openai import OpenAI
from typing import Optional, Callable
import os
import json
import time

class StockAssistant:
    def __init__(self, client: OpenAI, name: str, instructions: str):
        self.client = client
        self.name = name
        
        # Check for existing assistant
        existing = None
        try:
            assistants = self.client.beta.assistants.list(limit=100)
            existing = next((a for a in assistants.data if a.name == name), None)
        except Exception as e:
            print(f"Error listing assistants: {str(e)}")
        
        if existing:
            self.assistant = existing
        else:
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
                model="gpt-4o"
            )

    async def analyze(self, thread_id: str, research_data: dict, 
                     opponent_last_msg: str = None, 
                     stream_handler: Optional[Callable] = None) -> str:
        """Run analysis using streaming API with opponent context"""
        try:
            # Prepare optimized message
            message = {
                "meta": {
                    "ticker": research_data.get('ticker', ''),
                    "agent_type": self.name,
                    "round": research_data.get('round', 0)
                },
                "research": {
                    "metrics": research_data.get('metrics', {}),
                    "news": research_data.get('news', [])
                },
                "opponent_argument": opponent_last_msg
            }

            # Post message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=json.dumps(message, separators=(',', ':'))
            )

            # Start streaming run with timeout
            full_response = ""
            try:
                with self.client.beta.threads.runs.stream(
                    thread_id=thread_id,
                    assistant_id=self.assistant.id,
                    timeout=30  # 30 second timeout
                ) as stream:
                    for event in stream:
                        if event.event == 'thread.message.delta':
                            content = event.data.delta.content[0].text.value
                            full_response += content
                            if stream_handler:
                                stream_handler(content)
                        elif event.event == 'thread.run.failed':
                            raise Exception(f"Run failed: {event.data.last_error}")
                            
                    return full_response

            except Exception as e:
                # Cancel any stuck run before re-raising
                try:
                    self.client.beta.threads.runs.cancel(
                        thread_id=thread_id,
                        run_id=stream.run.id
                    )
                except Exception:
                    pass
                raise

        except Exception as e:
            print(f"Error in {self.name} analysis: {str(e)}")
            return ""

class BullishAssistant(StockAssistant):
    def __init__(self, client: OpenAI):
        instructions = """You are a bullish stock analyst specializing in identifying:
- Strong fundamentals (P/E ratios, revenue growth, profit margins)  
- Competitive advantages (moats, market position, patents)
- Growth catalysts (new markets, products, partnerships)
- Potential risks (but emphasize why they're manageable)

Structure responses clearly with:
1. Investment thesis summary
2. Key quantitative metrics  
3. Qualitative strengths
4. Risk assessment"""
        super().__init__(client, "Bullish Analyst", instructions)

class BearishAssistant(StockAssistant):
    def __init__(self, client: OpenAI):
        instructions = """You are a bearish stock analyst specializing in identifying:
- Overvaluation metrics (P/E vs sector, PEG ratio)  
- Deteriorating fundamentals (declining margins, slowing growth)  
- Competitive threats (market share loss, disruption risks)
- Management/execution risks  

Structure responses clearly with:
1. Risk thesis summary  
2. Warning metrics  
3. Competitive threats  
4. Bull case rebuttal"""
        super().__init__(client, "Bearish Analyst", instructions)
