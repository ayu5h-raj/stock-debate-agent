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
        
        client = AsyncOpenAI(api_key=self.api_key, api_version="2023-03-15")
        
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
        
    async def run_debate(self, agents: list, turns: int, topic: str, context: str = "", stream_handler=None) -> Dict[str, Any]:
        """Simulate a debate between agents with optional streaming and context"""
        messages = []
        current_topic = topic # Initial topic
        if context:
             current_topic += f"\n\nRelevant Context:\n{context}" # Add context for the first turn

        for i in range(turns):
            for agent in agents:
                # Use the potentially updated topic (including context for first turn)
                # Pass full context only on first turn, subsequent turns use original topic + history
                current_prompt = current_topic if i == 0 else topic 
                
                # Add previous messages as history for context in subsequent turns
                history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
                if history and i > 0:
                    current_prompt += f"\n\nPrevious Discussion:\n{history}"

                if stream_handler:
                    # Stream the response
                    stream = await agent.generate_response(current_prompt, stream=True)
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
                    response = await agent.generate_response(current_prompt)
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
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), api_version="2023-03-15")
        
        conclusion_response = await client.chat.completions.create(
            model="gpt-4o-mini",
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
