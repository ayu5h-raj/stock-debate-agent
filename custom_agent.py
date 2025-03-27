import os
from typing import Optional, Dict, Any

class Agent:
    def __init__(self, 
                 name: str,
                 persona: str,
                 system_prompt: str,
                 tools: Optional[list] = None):
        self.name = name
        self.persona = persona
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.api_key = os.getenv("OPENAI_API_KEY")
        
    async def generate_response(self, prompt: str, max_tokens: int = 1000, stream: bool = False):
        """Generate response using OpenAI API"""
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.api_key)
        
        if stream:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
                stream=True
            )
            return response
        else:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content

class AgentSystem:
    def __init__(self):
        self.agents = []
        
    def register_agent(self, agent: Agent):
        self.agents.append(agent)
        
    async def run_debate(self, agents: list, turns: int, topic: str, stream_handler=None) -> Dict[str, Any]:
        """Simulate a debate between agents with optional streaming"""
        messages = []
        for i in range(turns):
            for agent in agents:
                if stream_handler:
                    # Stream the response
                    stream = await agent.generate_response(topic, stream=True)
                    full_response = ""
                    async for chunk in stream:
                        content = chunk.choices[0].delta.content
                        if content:
                            full_response += content
                            await stream_handler(agent.name, content)
                    messages.append({
                        'role': agent.name,
                        'content': full_response
                    })
                else:
                    # Non-streaming response
                    response = await agent.generate_response(topic)
                    messages.append({
                        'role': agent.name,
                        'content': response
                    })
        # Add a final step to generate a conclusion
        conclusion_prompt = f"Based on the following debate about {topic}, decide whether to buy, sell, or hold the stock. Provide a brief justification.\n\nDebate:\n"
        for msg in messages:
            conclusion_prompt += f"{msg['role']}: {msg['content']}\n"
            
        # Use a neutral system prompt for the conclusion
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        conclusion_response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a neutral financial analyst summarizing a debate."},
                {"role": "user", "content": conclusion_prompt}
            ],
            max_tokens=150,
            temperature=0.5
        )
        final_conclusion = conclusion_response.choices[0].message.content

        return {
            'messages': messages,
            'summary': f"Debate concluded after {turns} turns per agent.",
            'conclusion': final_conclusion
        }
