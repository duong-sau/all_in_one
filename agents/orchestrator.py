from typing import Dict, List, Callable
from agents.specialized_agents import (
    IdeationAgent, DesignAgent, CodingAgent,
    TestingAgent, ResearchAgent, DocumentationAgent
)
from utils.llm_client import LLMClient

class TaskOrchestrator:
    def __init__(self, llm_client: LLMClient, model: str = "gpt-4o-mini"):
        self.llm_client = llm_client
        self.agents = {
            "ideation": IdeationAgent(llm_client, model),
            "design": DesignAgent(llm_client, model),
            "coding": CodingAgent(llm_client, model),
            "testing": TestingAgent(llm_client, model),
            "research": ResearchAgent(llm_client, model),
            "documentation": DocumentationAgent(llm_client, model)
        }
        self.task_results = {}
    
    def execute_plan(self, plan: Dict, context: Dict, progress_callback: Callable = None) -> List[Dict]:
        all_results = []
        total_tasks = sum(len(phase.get("tasks", [])) for phase in plan.get("phases", []))
        completed_tasks = 0
        
        for phase in plan.get("phases", []):
            phase_name = phase.get("name", "Unknown Phase")
            
            if progress_callback:
                progress_callback(f"🔄 Bắt đầu phase: {phase_name}", completed_tasks / total_tasks if total_tasks > 0 else 0)
            
            for task in phase.get("tasks", []):
                task_id = task.get("task_id", "unknown")
                assigned_agent = task.get("assigned_agent", "research")
                
                if progress_callback:
                    progress_callback(f"⚙️ Đang thực hiện: {task.get('name', 'Unknown Task')} (Agent: {assigned_agent})", 
                                    completed_tasks / total_tasks if total_tasks > 0 else 0)
                
                agent = self.agents.get(assigned_agent)
                if agent:
                    result = agent.execute_task(task, context)
                    self.task_results[task_id] = result
                    all_results.append(result)
                else:
                    all_results.append({
                        "task_id": task_id,
                        "agent_type": assigned_agent,
                        "status": "failed",
                        "result": f"Agent {assigned_agent} không tồn tại"
                    })
                
                completed_tasks += 1
                if progress_callback:
                    progress_callback(f"✅ Hoàn thành: {task.get('name', 'Unknown Task')}", 
                                    completed_tasks / total_tasks if total_tasks > 0 else 0)
        
        return all_results
    
    def generate_final_report(self, idea: Dict, plan: Dict, results: List[Dict]) -> str:
        doc_agent = self.agents["documentation"]
        
        report_task = {
            "task_id": "final_report",
            "name": "Tạo báo cáo tổng kết dự án",
            "description": f"""Tạo một báo cáo chi tiết về dự án với các thông tin sau:
            
Ý TƯỞNG DỰ ÁN:
{idea}

KẾ HOẠCH:
{plan}

KẾT QUẢ THỰC HIỆN:
{len(results)} tasks đã hoàn thành

Hãy tạo một báo cáo toàn diện với các phần:
1. Tóm tắt Executive Summary
2. Tổng quan dự án
3. Kết quả chi tiết từng phase
4. Kết luận và đề xuất bước tiếp theo
"""
        }
        
        report_result = doc_agent.execute_task(report_task, {"idea": idea, "plan": plan, "results": results})
        return report_result.get("result", "Không thể tạo báo cáo")
