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
        if 'task_states' in st.session_state:
            st.session_state.task_states = {}
        if 'orchestrator' in st.session_state:
            st.session_state.orchestrator = None
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
            st.markdown(f"**👥 Đối tượng người dùng:** {idea.get('target_users', 'N/A')}")
        
        with col2:
            st.markdown(f"**💎 Giá trị cốt lõi:** {idea.get('value_proposition', 'N/A')}")
        
        st.divider()
        
        st.markdown("### 🎯 Tính năng chính")
        st.markdown("*Bạn có thể thêm, sửa hoặc xóa các tính năng*")
        
        if 'key_features' not in idea:
            idea['key_features'] = []
        
        features = idea.get('key_features', [])
        
        for idx, feature in enumerate(features):
            col_feature, col_delete = st.columns([5, 1])
            with col_feature:
                new_value = st.text_input(
                    f"Tính năng {idx + 1}",
                    value=feature,
                    key=f"feature_{idx}",
                    label_visibility="collapsed"
                )
                if new_value != feature:
                    st.session_state.idea['key_features'][idx] = new_value
            
            with col_delete:
                if st.button("🗑️", key=f"delete_feature_{idx}", help="Xóa tính năng này"):
                    st.session_state.idea['key_features'].pop(idx)
                    st.rerun()
        
        new_feature = st.text_input("➕ Thêm tính năng mới", key="new_feature", placeholder="Nhập tính năng mới...")
        if st.button("Thêm tính năng", key="add_feature_btn"):
            if new_feature and new_feature.strip():
                if 'key_features' not in st.session_state.idea:
                    st.session_state.idea['key_features'] = []
                st.session_state.idea['key_features'].append(new_feature.strip())
                st.rerun()
        
        st.divider()
        
        st.markdown("### 🛠️ Công nghệ đề xuất")
        st.markdown("*Bạn có thể thêm, sửa hoặc xóa các công nghệ*")
        
        if 'tech_stack_suggestions' not in idea:
            idea['tech_stack_suggestions'] = []
        
        tech_stack = idea.get('tech_stack_suggestions', [])
        
        for idx, tech in enumerate(tech_stack):
            col_tech, col_delete = st.columns([5, 1])
            with col_tech:
                new_value = st.text_input(
                    f"Công nghệ {idx + 1}",
                    value=tech,
                    key=f"tech_{idx}",
                    label_visibility="collapsed"
                )
                if new_value != tech:
                    st.session_state.idea['tech_stack_suggestions'][idx] = new_value
            
            with col_delete:
                if st.button("🗑️", key=f"delete_tech_{idx}", help="Xóa công nghệ này"):
                    st.session_state.idea['tech_stack_suggestions'].pop(idx)
                    st.rerun()
        
        new_tech = st.text_input("➕ Thêm công nghệ mới", key="new_tech", placeholder="Nhập công nghệ mới...")
        if st.button("Thêm công nghệ", key="add_tech_btn"):
            if new_tech and new_tech.strip():
                if 'tech_stack_suggestions' not in st.session_state.idea:
                    st.session_state.idea['tech_stack_suggestions'] = []
                st.session_state.idea['tech_stack_suggestions'].append(new_tech.strip())
                st.rerun()
        
        st.divider()
        
        col1, col2 = st.columns([1, 4])
        with col1:
            create_plan_btn = st.button("📋 Tạo kế hoạch", type="primary")
        
        if create_plan_btn and st.session_state.llm_client:
            try:
                with st.spinner("📋 AI đang tạo kế hoạch chi tiết..."):
                    master_agent = MasterAgent(st.session_state.llm_client, st.session_state.master_model)
                    st.session_state.plan = master_agent.create_project_plan(st.session_state.idea)
                    if 'task_states' in st.session_state:
                        st.session_state.task_states = {}
                    if 'orchestrator' in st.session_state:
                        st.session_state.orchestrator = None
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
    st.header("⚙️ Bảng điều khiển thực thi")
    
    if st.session_state.plan:
        if 'task_states' not in st.session_state:
            st.session_state.task_states = {}
        
        if 'orchestrator' not in st.session_state:
            st.session_state.orchestrator = TaskOrchestrator(st.session_state.llm_client, st.session_state.worker_model) if st.session_state.llm_client else None
        
        context = {
            "idea": st.session_state.idea,
            "plan": st.session_state.plan
        }
        
        st.markdown("*Bạn có thể thực thi từng task riêng lẻ, thêm ghi chú và thực thi lại nếu cần*")
        st.divider()
        
        all_tasks = []
        for phase_idx, phase in enumerate(st.session_state.plan.get('phases', [])):
            st.subheader(f"📦 Phase {phase_idx + 1}: {phase.get('name', 'Unknown')}")
            st.markdown(f"*{phase.get('description', '')}*")
            
            tasks = phase.get('tasks', [])
            for task_idx, task in enumerate(tasks):
                task_id = task.get('task_id', f"phase{phase_idx}_task{task_idx}")
                task_name = task.get('name', 'Unknown Task')
                task_desc = task.get('description', '')
                assigned_agent = task.get('assigned_agent', 'research')
                
                if task_id not in st.session_state.task_states:
                    st.session_state.task_states[task_id] = {
                        'status': 'pending',
                        'result': None,
                        'notes': ''
                    }
                
                task_state = st.session_state.task_states[task_id]
                
                with st.container():
                    st.markdown(f"### 🎯 {task_name}")
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        status_emoji = {
                            'pending': '⏳ Chờ thực thi',
                            'running': '⚙️ Đang chạy...',
                            'completed': '✅ Hoàn thành',
                            'failed': '❌ Thất bại'
                        }
                        st.markdown(f"**Trạng thái:** {status_emoji.get(task_state['status'], 'Unknown')}")
                        st.markdown(f"**Agent:** `{assigned_agent}`")
                    
                    with col2:
                        if task_state['status'] == 'pending' or task_state['status'] == 'failed':
                            if st.button(f"▶️ Thực thi", key=f"exec_{task_id}", type="primary"):
                                st.session_state.task_states[task_id]['status'] = 'running'
                                st.rerun()
                    
                    with col3:
                        if task_state['status'] == 'completed':
                            if st.button(f"🔄 Thực thi lại", key=f"reexec_{task_id}"):
                                st.session_state.task_states[task_id]['status'] = 'running'
                                st.session_state.task_states[task_id]['result'] = None
                                st.rerun()
                    
                    if task_state['status'] == 'running' and st.session_state.orchestrator:
                        with st.spinner(f"⚙️ Đang thực thi task: {task_name}..."):
                            try:
                                result = st.session_state.orchestrator.execute_single_task(task, context)
                                st.session_state.task_states[task_id]['status'] = 'completed'
                                st.session_state.task_states[task_id]['result'] = result
                                st.success(f"✅ Hoàn thành task: {task_name}")
                                st.rerun()
                            except Exception as e:
                                st.session_state.task_states[task_id]['status'] = 'failed'
                                st.session_state.task_states[task_id]['result'] = {
                                    'task_id': task_id,
                                    'status': 'failed',
                                    'result': str(e)
                                }
                                st.error(f"❌ Lỗi: {str(e)}")
                    
                    with st.expander("📝 Mô tả & Chi tiết"):
                        st.markdown(f"**Mô tả task:** {task_desc}")
                        if task.get('estimated_duration'):
                            st.markdown(f"**Thời gian ước tính:** {task['estimated_duration']}")
                        if task.get('dependencies'):
                            st.markdown(f"**Phụ thuộc:** {', '.join(task['dependencies'])}")
                    
                    if task_state['result']:
                        with st.expander("📊 Kết quả", expanded=True):
                            st.markdown(task_state['result'].get('result', 'N/A'))
                    
                    notes = st.text_area(
                        "💭 Ghi chú của bạn",
                        value=task_state['notes'],
                        key=f"notes_{task_id}",
                        placeholder="Thêm ghi chú về task này...",
                        height=80
                    )
                    if notes != task_state['notes']:
                        st.session_state.task_states[task_id]['notes'] = notes
                    
                    st.divider()
        
        st.divider()
        completed_tasks = sum(1 for state in st.session_state.task_states.values() if state['status'] == 'completed')
        total_tasks = len(st.session_state.task_states)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tổng số tasks", total_tasks)
        with col2:
            st.metric("Đã hoàn thành", completed_tasks)
        with col3:
            progress_pct = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            st.metric("Tiến độ", f"{progress_pct:.0f}%")
        
        if completed_tasks == total_tasks and total_tasks > 0:
            st.success("🎉 Đã hoàn thành tất cả tasks!")
            
            if st.button("📄 Tạo báo cáo tổng kết", type="primary"):
                if st.session_state.orchestrator and st.session_state.idea and st.session_state.plan:
                    with st.spinner("📄 Đang tạo báo cáo..."):
                        results = [state['result'] for state in st.session_state.task_states.values() if state['result']]
                        st.session_state.report = st.session_state.orchestrator.generate_final_report(
                            st.session_state.idea,
                            st.session_state.plan,
                            results
                        )
                        st.balloons()
                        st.success("✅ Đã tạo báo cáo! Xem tại tab 'Báo cáo'")
    else:
        st.info("ℹ️ Vui lòng tạo kế hoạch ở tab 'Kế hoạch' trước khi thực thi.")

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
