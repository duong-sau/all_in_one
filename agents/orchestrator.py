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
    
    def execute_plan(self, plan: Dict, context: Dict, progress_callback: Callable | None = None) -> List[Dict]:
        if not plan or not isinstance(plan, dict):
            raise ValueError("Kế hoạch không hợp lệ hoặc rỗng")
        
        phases = plan.get("phases", [])
        if not phases or not isinstance(phases, list):
            raise ValueError("Kế hoạch không chứa phases hợp lệ. Vui lòng tạo lại kế hoạch.")
        
        all_results = []
        total_tasks = sum(len(phase.get("tasks", [])) for phase in phases)
        
        if total_tasks == 0:
            raise ValueError("Kế hoạch không chứa tasks nào. Vui lòng tạo lại kế hoạch với các tasks cụ thể.")
        
        completed_tasks = 0
        
        for phase in phases:
            phase_name = phase.get("name", "Unknown Phase")
            tasks = phase.get("tasks", [])
            
            if not tasks:
                continue
            
            if progress_callback:
                progress_callback(f"🔄 Bắt đầu phase: {phase_name}", completed_tasks / total_tasks)
            
            for task in tasks:
                task_id = task.get("task_id", "unknown")
                task_name = task.get("name", "Unknown Task")
                assigned_agent = task.get("assigned_agent", "research")
                
                if progress_callback:
                    progress_callback(f"⚙️ Đang thực hiện: {task_name} (Agent: {assigned_agent})", 
                                    completed_tasks / total_tasks)
                
                try:
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
                except Exception as e:
                    all_results.append({
                        "task_id": task_id,
                        "agent_type": assigned_agent,
                        "status": "failed",
                        "result": f"Lỗi khi thực hiện task: {str(e)}"
                    })
                
                completed_tasks += 1
                if progress_callback:
                    progress_callback(f"✅ Hoàn thành: {task_name}", completed_tasks / total_tasks)
        
        return all_results
    
    def execute_single_task(self, task: Dict, context: Dict) -> Dict:
        task_id = task.get("task_id", "unknown")
        task_name = task.get("name", "Unknown Task")
        assigned_agent = task.get("assigned_agent", "research")
        
        try:
            agent = self.agents.get(assigned_agent)
            if agent:
                result = agent.execute_task(task, context)
                self.task_results[task_id] = result
                return result
            else:
                return {
                    "task_id": task_id,
                    "agent_type": assigned_agent,
                    "status": "failed",
                    "result": f"Agent {assigned_agent} không tồn tại"
                }
        except Exception as e:
            return {
                "task_id": task_id,
                "agent_type": assigned_agent,
                "status": "failed",
                "result": f"Lỗi khi thực hiện task: {str(e)}"
            }
    
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
