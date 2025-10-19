from typing import Dict, List
import json
from utils.llm_client import LLMClient

class MasterAgent:
    def __init__(self, llm_client: LLMClient, model: str = "gpt-4o"):
        self.llm_client = llm_client
        self.model = model
    
    def generate_idea(self, project_description: str) -> Dict:
        prompt = f"""Bạn là một chuyên gia tư vấn phát triển sản phẩm. Hãy phân tích yêu cầu dự án và tạo ra ý tưởng chi tiết.

YÊU CẦU DỰ ÁN:
{project_description}

Hãy trả về kết quả dưới dạng JSON với cấu trúc sau:
{{
    "project_name": "Tên dự án",
    "overview": "Tổng quan về dự án",
    "key_features": ["Tính năng 1", "Tính năng 2", ...],
    "target_users": "Đối tượng người dùng",
    "value_proposition": "Giá trị cốt lõi",
    "tech_stack_suggestions": ["Công nghệ 1", "Công nghệ 2", ...]
}}"""
        
        messages = [
            {"role": "system", "content": "Bạn là chuyên gia tư vấn sản phẩm. Luôn trả về JSON hợp lệ."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm_client.chat(messages, model=self.model, temperature=0.8)
        
        try:
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            return json.loads(response_clean.strip())
        except json.JSONDecodeError:
            return {
                "project_name": "Dự án mới",
                "overview": response,
                "key_features": [],
                "target_users": "Chưa xác định",
                "value_proposition": "Chưa xác định",
                "tech_stack_suggestions": []
            }
    
    def create_project_plan(self, idea: Dict) -> Dict:
        prompt = f"""Dựa trên ý tưởng dự án sau, hãy tạo một kế hoạch thực hiện chi tiết:

Ý TƯỞNG DỰ ÁN:
{json.dumps(idea, ensure_ascii=False, indent=2)}

Hãy tạo kế hoạch với các phase và tasks cụ thể. Trả về JSON với cấu trúc:
{{
    "phases": [
        {{
            "name": "Tên phase",
            "description": "Mô tả",
            "tasks": [
                {{
                    "task_id": "unique_id",
                    "name": "Tên task",
                    "description": "Mô tả chi tiết",
                    "assigned_agent": "ideation/design/coding/testing/research/documentation",
                    "estimated_duration": "Thời gian dự kiến",
                    "dependencies": ["task_id khác nếu có"]
                }}
            ]
        }}
    ],
    "timeline": "Tổng thời gian dự kiến",
    "resources_needed": ["Resource 1", "Resource 2", ...]
}}"""
        
        messages = [
            {"role": "system", "content": "Bạn là project manager chuyên nghiệp. Luôn trả về JSON hợp lệ."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm_client.chat(messages, model=self.model, temperature=0.7, max_tokens=4000)
        
        try:
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            return json.loads(response_clean.strip())
        except json.JSONDecodeError:
            return {
                "phases": [],
                "timeline": "Chưa xác định",
                "resources_needed": []
            }
