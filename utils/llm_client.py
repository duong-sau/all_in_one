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
        try:
            if model.startswith("gpt") or model.startswith("o1"):
                if not self.openai_client:
                    raise ValueError("OpenAI API key chưa được cấu hình. Vui lòng thêm API key ở sidebar.")
                
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,  # type: ignore
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                content = response.choices[0].message.content
                return content if content else ""
            
            elif model.startswith("claude"):
                if not self.anthropic_client:
                    raise ValueError("Anthropic API key chưa được cấu hình. Vui lòng thêm API key ở sidebar.")
                
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
                    system=system_message if system_message else "",
                    messages=user_messages  # type: ignore
                )
                
                for block in response.content:
                    if hasattr(block, 'text'):
                        return block.text
                return ""
            
            else:
                raise ValueError(f"Model không được hỗ trợ: {model}")
        
        except ValueError as e:
            raise e
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                raise ValueError(f"Lỗi xác thực API: {error_msg}. Vui lòng kiểm tra lại API key.")
            elif "rate" in error_msg.lower() or "quota" in error_msg.lower():
                raise ValueError(f"Lỗi giới hạn API: {error_msg}. Bạn có thể đã vượt quá giới hạn hoặc hết quota.")
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                raise ValueError(f"Lỗi kết nối mạng: {error_msg}. Vui lòng kiểm tra kết nối internet.")
            else:
                raise ValueError(f"Lỗi từ LLM API: {error_msg}")
    
    def available_models(self) -> List[str]:
        models = []
        if self.openai_client:
            models.extend(["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-preview", "o1-mini"])
        if self.anthropic_client:
            models.extend(["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"])
        return models
