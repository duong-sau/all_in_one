import os
from typing import List, Dict, Optional
from openai import OpenAI
from anthropic import Anthropic

class LLMClient:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
        if anthropic_key:
            self.anthropic_client = Anthropic(api_key=anthropic_key)
    
    def chat(self, messages: List[Dict[str, str]], model: str = "gpt-4o", temperature: float = 0.7, max_tokens: int = 4000) -> str:
        if model.startswith("gpt") or model.startswith("o1"):
            if not self.openai_client:
                raise ValueError("OpenAI API key not configured")
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        elif model.startswith("claude"):
            if not self.anthropic_client:
                raise ValueError("Anthropic API key not configured")
            
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message if system_message else None,
                messages=user_messages
            )
            return response.content[0].text
        
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    def available_models(self) -> List[str]:
        models = []
        if self.openai_client:
            models.extend(["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-preview", "o1-mini"])
        if self.anthropic_client:
            models.extend(["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"])
        return models
