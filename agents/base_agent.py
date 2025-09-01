"""
Base Agent class for all specialized agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent(ABC):
    """Base class for all agents with common functionality"""
    
    def __init__(self, model: str = "gpt-4o"):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = model
    
    def call_llm(self, messages: list, temperature: float = 0.3) -> str:
        """Make a call to the LLM with the given messages"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=300  # Slightly reduced for more concise responses
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM Error: {str(e)}")
            return f"Error calling LLM: {str(e)}"
    
    @abstractmethod
    def process_request(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a request and return a response"""
        pass