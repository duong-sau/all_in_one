from typing import Dict, List
from utils.llm_client import LLMClient

class SpecializedAgent:
    def __init__(self, llm_client: LLMClient, agent_type: str, model: str = "gpt-4o-mini"):
        self.llm_client = llm_client
        self.agent_type = agent_type
        self.model = model
        self.system_prompts = {
            "ideation": "Bạn là chuyên gia sáng tạo ý tưởng. Nhiệm vụ của bạn là phát triển và mở rộng ý tưởng sản phẩm.",
            "design": "Bạn là UI/UX designer chuyên nghiệp. Nhiệm vụ của bạn là thiết kế giao diện và trải nghiệm người dùng.",
            "coding": "Bạn là senior software engineer. Nhiệm vụ của bạn là viết code chất lượng cao, clean và maintainable.",
            "testing": "Bạn là QA engineer chuyên nghiệp. Nhiệm vụ của bạn là tạo test cases và tìm bugs.",
            "research": "Bạn là research specialist. Nhiệm vụ của bạn là tìm kiếm và tổng hợp thông tin từ các nguồn đáng tin cậy.",
            "documentation": "Bạn là technical writer. Nhiệm vụ của bạn là viết tài liệu kỹ thuật rõ ràng và dễ hiểu."
        }
    
    def execute_task(self, task: Dict, context: Dict = None) -> Dict:
        system_prompt = self.system_prompts.get(self.agent_type, "Bạn là AI assistant chuyên nghiệp.")
        
        context_str = ""
        if context:
            context_str = f"\n\nNGỮ CẢNH DỰ ÁN:\n{context}"
        
        prompt = f"""NHIỆM VỤ:
Tên: {task.get('name', 'Không có tên')}
Mô tả: {task.get('description', 'Không có mô tả')}
{context_str}

Hãy thực hiện nhiệm vụ này một cách chi tiết và chuyên nghiệp. Trả về kết quả đầy đủ."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        result = self.llm_client.chat(messages, model=self.model, max_tokens=3000)
        
        return {
            "task_id": task.get("task_id", "unknown"),
            "agent_type": self.agent_type,
            "status": "completed",
            "result": result
        }


class IdeationAgent(SpecializedAgent):
    def __init__(self, llm_client: LLMClient, model: str = "gpt-4o-mini"):
        super().__init__(llm_client, "ideation", model)


class DesignAgent(SpecializedAgent):
    def __init__(self, llm_client: LLMClient, model: str = "gpt-4o-mini"):
        super().__init__(llm_client, "design", model)


class CodingAgent(SpecializedAgent):
    def __init__(self, llm_client: LLMClient, model: str = "gpt-4o-mini"):
        super().__init__(llm_client, "coding", model)


class TestingAgent(SpecializedAgent):
    def __init__(self, llm_client: LLMClient, model: str = "gpt-4o-mini"):
        super().__init__(llm_client, "testing", model)


class ResearchAgent(SpecializedAgent):
    def __init__(self, llm_client: LLMClient, model: str = "gpt-4o-mini"):
        super().__init__(llm_client, "research", model)


class DocumentationAgent(SpecializedAgent):
    def __init__(self, llm_client: LLMClient, model: str = "gpt-4o-mini"):
        super().__init__(llm_client, "documentation", model)
