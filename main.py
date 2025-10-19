import streamlit as st
import os
from utils.llm_client import LLMClient
from agents.master_agent import MasterAgent
from agents.orchestrator import TaskOrchestrator
import json

st.set_page_config(
    page_title="AI Project Automation",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Project Automation System")
st.markdown("### Hệ thống tự động hóa quy trình phát triển dự án bằng AI")

if "llm_client" not in st.session_state:
    st.session_state.llm_client = None

if "master_model" not in st.session_state:
    st.session_state.master_model = "gpt-4o"

if "worker_model" not in st.session_state:
    st.session_state.worker_model = "gpt-4o-mini"

if "idea" not in st.session_state:
    st.session_state.idea = None

if "plan" not in st.session_state:
    st.session_state.plan = None

if "results" not in st.session_state:
    st.session_state.results = None

if "report" not in st.session_state:
    st.session_state.report = None

with st.sidebar:
    st.header("⚙️ Cấu hình")
    
    st.subheader("API Keys")
    openai_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    anthropic_key = st.text_input("Anthropic API Key", type="password", value=os.getenv("ANTHROPIC_API_KEY", ""))
    
    if st.button("💾 Lưu API Keys"):
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        st.session_state.llm_client = LLMClient()
        st.success("✅ Đã lưu API keys!")
    
    if st.session_state.llm_client:
        st.success("✅ LLM Client đã sẵn sàng")
        available_models = st.session_state.llm_client.available_models()
        
        if available_models:
            st.subheader("Model Selection")
            st.session_state.master_model = st.selectbox(
                "Master Agent Model (planning)",
                available_models,
                index=0 if "gpt-4o" in available_models else 0
            )
            
            st.session_state.worker_model = st.selectbox(
                "Worker Agent Model (execution)",
                available_models,
                index=available_models.index("gpt-4o-mini") if "gpt-4o-mini" in available_models else 0
            )
    else:
        st.warning("⚠️ Vui lòng cấu hình API keys")
    
    st.divider()
    
    if st.button("🔄 Reset toàn bộ"):
        st.session_state.idea = None
        st.session_state.plan = None
        st.session_state.results = None
        st.session_state.report = None
        st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Mô tả dự án", 
    "💡 Ý tưởng", 
    "📋 Kế hoạch", 
    "⚙️ Thực thi", 
    "📄 Báo cáo"
])

with tab1:
    st.header("📝 Mô tả dự án của bạn")
    st.markdown("Hãy mô tả dự án bạn muốn thực hiện. AI sẽ tự động lên ý tưởng, tạo kế hoạch và thực hiện.")
    
    project_description = st.text_area(
        "Mô tả dự án:",
        height=200,
        placeholder="Ví dụ: Tôi muốn xây dựng một ứng dụng web để quản lý công việc hàng ngày, có tính năng reminder, phân loại task theo mức độ ưu tiên..."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        generate_idea_btn = st.button("🚀 Tạo ý tưởng", type="primary", disabled=not st.session_state.llm_client)
    
    if generate_idea_btn and project_description and st.session_state.llm_client:
        try:
            with st.spinner("🤔 AI đang phân tích và tạo ý tưởng..."):
                master_agent = MasterAgent(st.session_state.llm_client, st.session_state.master_model)
                st.session_state.idea = master_agent.generate_idea(project_description)
                st.success("✅ Đã tạo ý tưởng!")
                st.rerun()
        except ValueError as e:
            st.error(f"❌ {str(e)}")
        except Exception as e:
            st.error(f"❌ Lỗi không mong đợi: {str(e)}")

with tab2:
    st.header("💡 Ý tưởng dự án")
    
    if st.session_state.idea:
        idea = st.session_state.idea
        
        st.subheader(f"🎯 {idea.get('project_name', 'Dự án mới')}")
        st.markdown(f"**Tổng quan:** {idea.get('overview', 'N/A')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Tính năng chính:**")
            for feature in idea.get('key_features', []):
                st.markdown(f"- {feature}")
        
        with col2:
            st.markdown(f"**👥 Đối tượng người dùng:** {idea.get('target_users', 'N/A')}")
            st.markdown(f"**💎 Giá trị cốt lõi:** {idea.get('value_proposition', 'N/A')}")
        
        st.markdown("**🛠️ Công nghệ đề xuất:**")
        for tech in idea.get('tech_stack_suggestions', []):
            st.markdown(f"- {tech}")
        
        st.divider()
        
        col1, col2 = st.columns([1, 4])
        with col1:
            create_plan_btn = st.button("📋 Tạo kế hoạch", type="primary")
        
        if create_plan_btn and st.session_state.llm_client:
            try:
                with st.spinner("📋 AI đang tạo kế hoạch chi tiết..."):
                    master_agent = MasterAgent(st.session_state.llm_client, st.session_state.master_model)
                    st.session_state.plan = master_agent.create_project_plan(st.session_state.idea)
                    st.success("✅ Đã tạo kế hoạch!")
                    st.rerun()
            except ValueError as e:
                st.error(f"❌ {str(e)}")
            except Exception as e:
                st.error(f"❌ Lỗi không mong đợi: {str(e)}")
    else:
        st.info("ℹ️ Vui lòng tạo ý tưởng ở tab 'Mô tả dự án' trước.")

with tab3:
    st.header("📋 Kế hoạch thực hiện")
    
    if st.session_state.plan:
        plan = st.session_state.plan
        
        st.markdown(f"**⏰ Timeline:** {plan.get('timeline', 'N/A')}")
        
        st.markdown("**📦 Resources cần thiết:**")
        for resource in plan.get('resources_needed', []):
            st.markdown(f"- {resource}")
        
        st.divider()
        st.subheader("📊 Các Phase thực hiện")
        
        for i, phase in enumerate(plan.get('phases', []), 1):
            with st.expander(f"Phase {i}: {phase.get('name', 'Unknown')}", expanded=i==1):
                st.markdown(f"**Mô tả:** {phase.get('description', 'N/A')}")
                
                st.markdown("**Tasks:**")
                for j, task in enumerate(phase.get('tasks', []), 1):
                    st.markdown(f"{j}. **{task.get('name', 'Unknown')}** (Agent: `{task.get('assigned_agent', 'unknown')}`)")
                    st.markdown(f"   - {task.get('description', 'N/A')}")
                    st.markdown(f"   - Thời gian: {task.get('estimated_duration', 'N/A')}")
                    if task.get('dependencies'):
                        st.markdown(f"   - Phụ thuộc: {', '.join(task['dependencies'])}")
        
        st.divider()
        
        col1, col2 = st.columns([1, 4])
        with col1:
            execute_plan_btn = st.button("▶️ Bắt đầu thực thi", type="primary")
        
        if execute_plan_btn:
            st.session_state.execute_triggered = True
            st.rerun()
    else:
        st.info("ℹ️ Vui lòng tạo kế hoạch ở tab 'Ý tưởng' trước.")

with tab4:
    st.header("⚙️ Thực thi kế hoạch")
    
    if hasattr(st.session_state, 'execute_triggered') and st.session_state.execute_triggered:
        if not st.session_state.results and st.session_state.llm_client and st.session_state.plan:
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(message, progress):
                    status_text.markdown(f"**{message}**")
                    progress_bar.progress(min(progress, 1.0))
                
                orchestrator = TaskOrchestrator(st.session_state.llm_client, st.session_state.worker_model)
                
                context = {
                    "idea": st.session_state.idea,
                    "plan": st.session_state.plan
                }
                
                st.session_state.results = orchestrator.execute_plan(
                    st.session_state.plan, 
                    context,
                    update_progress
                )
                
                status_text.markdown("**✅ Hoàn thành tất cả tasks!**")
                progress_bar.progress(1.0)
                
                if st.session_state.idea and st.session_state.plan and st.session_state.results:
                    with st.spinner("📄 Đang tạo báo cáo tổng kết..."):
                        st.session_state.report = orchestrator.generate_final_report(
                            st.session_state.idea,
                            st.session_state.plan,
                            st.session_state.results
                        )
                
                st.success("✅ Đã hoàn thành toàn bộ quy trình!")
                st.balloons()
            except ValueError as e:
                st.error(f"❌ {str(e)}")
            except Exception as e:
                st.error(f"❌ Lỗi khi thực thi: {str(e)}")
    
    if st.session_state.results:
        st.subheader("📊 Kết quả thực thi")
        
        for i, result in enumerate(st.session_state.results, 1):
            with st.expander(f"Task {i}: {result.get('task_id', 'unknown')} - Agent: {result.get('agent_type', 'unknown')}", expanded=False):
                st.markdown(f"**Status:** {result.get('status', 'unknown')}")
                st.markdown("**Kết quả:**")
                st.markdown(result.get('result', 'N/A'))
    else:
        if st.session_state.plan:
            st.info("ℹ️ Nhấn nút 'Bắt đầu thực thi' ở tab 'Kế hoạch' để bắt đầu.")
        else:
            st.info("ℹ️ Vui lòng tạo kế hoạch trước khi thực thi.")

with tab5:
    st.header("📄 Báo cáo tổng kết")
    
    if st.session_state.report:
        st.markdown(st.session_state.report)
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.download_button(
                label="📥 Tải báo cáo (TXT)",
                data=st.session_state.report,
                file_name="project_report.txt",
                mime="text/plain"
            ):
                st.success("✅ Đã tải báo cáo!")
        
        with col2:
            full_data = {
                "idea": st.session_state.idea,
                "plan": st.session_state.plan,
                "results": st.session_state.results,
                "report": st.session_state.report
            }
            if st.download_button(
                label="📥 Tải dữ liệu đầy đủ (JSON)",
                data=json.dumps(full_data, ensure_ascii=False, indent=2),
                file_name="project_full_data.json",
                mime="application/json"
            ):
                st.success("✅ Đã tải dữ liệu!")
    else:
        st.info("ℹ️ Báo cáo sẽ được tạo sau khi hoàn thành thực thi.")

st.divider()
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit & AI")
