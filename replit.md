# AI Project Automation System

## 📋 Tổng quan dự án
Hệ thống tự động hóa toàn bộ quy trình phát triển dự án bằng AI - từ lên ý tưởng, thiết kế, coding, testing đến viết báo cáo.

## 🎯 Mục đích
Giúp developers tự động hóa quy trình làm việc với sự hỗ trợ của nhiều AI agents chuyên biệt, giảm thời gian và công sức trong việc lên kế hoạch và thực thi dự án.

## 🏗️ Kiến trúc hệ thống

### Components chính:
1. **Master Agent** - AI chính phụ trách:
   - Phân tích yêu cầu và tạo ý tưởng
   - Tạo kế hoạch thực hiện chi tiết
   
2. **Task Orchestrator** - Điều phối viên:
   - Phân phối tasks cho các specialized agents
   - Quản lý workflow và dependencies
   - Thu thập kết quả từ các agents
   
3. **Specialized Agents** (6 loại):
   - **IdeationAgent**: Phát triển và mở rộng ý tưởng
   - **DesignAgent**: Thiết kế UI/UX
   - **CodingAgent**: Viết code
   - **TestingAgent**: Tạo test cases và tìm bugs
   - **ResearchAgent**: Tìm kiếm và tổng hợp thông tin
   - **DocumentationAgent**: Viết tài liệu và báo cáo
   
4. **LLM Client** - Kết nối multi-LLM:
   - Hỗ trợ OpenAI (GPT-4, GPT-4o, o1, etc.)
   - Hỗ trợ Anthropic (Claude 3.5 Sonnet, Haiku, Opus)
   - Linh hoạt chọn model cho từng loại agent

5. **Streamlit Web Interface**:
   - Dashboard theo dõi tiến độ
   - Quản lý cấu hình API keys
   - Hiển thị kết quả và báo cáo

## 📁 Cấu trúc dự án
```
.
├── main.py                 # Streamlit app chính
├── utils/
│   └── llm_client.py      # Client kết nối LLM APIs
├── agents/
│   ├── master_agent.py    # Master AI Agent
│   ├── specialized_agents.py  # 6 Specialized Agents
│   └── orchestrator.py    # Task Orchestrator
├── .gitignore
├── pyproject.toml         # Dependencies
└── replit.md             # Documentation
```

## 🚀 Cách sử dụng

### 1. Cấu hình API Keys
- Vào sidebar, nhập OpenAI API Key và/hoặc Anthropic API Key
- Click "Lưu API Keys"

### 2. Chọn Models
- **Master Agent Model**: Model mạnh cho planning (khuyên dùng GPT-4o)
- **Worker Agent Model**: Model hiệu quả cho execution (khuyên dùng GPT-4o-mini)

### 3. Quy trình làm việc
1. **Tab "Mô tả dự án"**: Nhập mô tả dự án → Click "Tạo ý tưởng"
2. **Tab "Ý tưởng"**: Xem ý tưởng chi tiết → Click "Tạo kế hoạch"
3. **Tab "Kế hoạch"**: Xem kế hoạch chi tiết → Click "Bắt đầu thực thi"
4. **Tab "Thực thi"**: Theo dõi quá trình AI thực hiện từng task
5. **Tab "Báo cáo"**: Xem và tải báo cáo tổng kết

## 🛠️ Công nghệ
- **Frontend**: Streamlit
- **Backend**: Python 3.11
- **AI/LLM**: OpenAI API, Anthropic API
- **Dependencies**: streamlit, openai, anthropic, python-dotenv

## 📝 Ghi chú
- Hệ thống hỗ trợ nhiều LLM providers để tăng tính linh hoạt
- Có thể tùy chỉnh model cho từng loại agent
- Kết quả có thể export dưới dạng TXT hoặc JSON

## 🔄 Phiên bản hiện tại
- v1.0.0 - Initial release
- Date: October 19, 2025
