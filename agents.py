import os
from openai import AsyncOpenAI  # Use AsyncOpenAI for compatibility with async Streamlit
from typing import AsyncGenerator, List, Dict, Optional
import json

# Base class (optional, but good practice) - Can be simplified if only used here
class ChatAgent:
    def __init__(self, client: AsyncOpenAI, system_prompt: str = ""):
        self.client = client
        self.system_prompt = system_prompt
        self.model = "gpt-4o-mini" # Use gpt-4o-mini

    async def generate_response_stream(
        self, 
        conversation_history: List[Dict[str, str]], 
        research_data_str: Optional[str] = None,
        opponent_last_msg: Optional[str] = None,
        max_tokens: Optional[int] = 1024,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Generates a streaming response using Chat Completions."""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add research data string if provided
        if research_data_str:
            messages.append({"role": "user", "content": f"Current Research Data:\n{research_data_str}"}) 

        # Add existing history
        messages.extend(conversation_history)

        # Add opponent's last message if provided
        if opponent_last_msg:
            messages.append({"role": "user", "content": f"Opponent's Last Argument:\n{opponent_last_msg}"}) 

        # Add final instruction based on whether opponent message exists
        if opponent_last_msg:
            messages.append({"role": "user", "content": "Based on the research data and your opponent's last argument, present your concise analysis."})
        else:
             messages.append({"role": "user", "content": "Based on the research data, present your concise opening analysis."})

        # Log the number of messages being sent
        print(f"[{self.__class__.__name__}] Sending {len(messages)} messages to API.")

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content
        except Exception as e:
            error_message = f"Error during generation for {self.__class__.__name__}: {str(e)}"
            print(error_message)
            # Yield a user-friendly error message in the stream
            yield f"\n\n[Analysis failed: {str(e)}]\n"


class BullishChatAgent(ChatAgent):
    def __init__(self, client: AsyncOpenAI):
        system_prompt = """You are a bullish stock analyst. Your goal is to present a strong investment thesis for the given stock.
Focus on:
- Strong fundamentals (P/E ratios, revenue growth, profit margins). Cite specific data points from the research provided.
- Competitive advantages (moats, market position, patents).
- Growth catalysts (new markets, products, partnerships).
- Address potential risks but emphasize why they are manageable or outweighed by the positives.

Structure your response clearly:
1.  **Investment Thesis:** Summarize why this stock is a buy.
2.  **Quantitative Strength:** Highlight key positive metrics from the research.
3.  **Qualitative Edge:** Describe the company's non-numerical advantages.
4.  **Risk Mitigation:** Acknowledge risks and explain why the outlook remains bullish.

Respond directly to the user prompt and incorporate the provided research data. If an opponent's argument is provided, address it constructively within your bullish framework.

**IMPORTANT: Be concise. Focus on the 1-2 most impactful points for this turn of the debate.**"""
        super().__init__(client, system_prompt=system_prompt)

class BearishChatAgent(ChatAgent):
    def __init__(self, client: AsyncOpenAI):
        system_prompt = """You are a bearish stock analyst. Your goal is to present a strong case against investing in the given stock.
Focus on:
- Overvaluation metrics (high P/E vs sector, PEG ratio). Cite specific data points from the research provided.
- Deteriorating fundamentals (declining margins, slowing growth).
- Competitive threats (market share loss, disruption risks).
- Management/execution risks or red flags.

Structure your response clearly:
1.  **Risk Thesis:** Summarize why this stock is a sell or hold-at-best.
2.  **Quantitative Weakness:** Highlight key negative metrics or concerning trends from the research.
3.  **Competitive & Market Threats:** Describe external factors posing a risk.
4.  **Bull Case Rebuttal:** If an opponent's argument is provided, directly challenge its points using your bearish perspective and the data.

Respond directly to the user prompt and incorporate the provided research data. Emphasize the risks and downsides.

**IMPORTANT: Be concise. Focus on the 1-2 most impactful points for this turn of the debate.**"""
        super().__init__(client, system_prompt=system_prompt)
