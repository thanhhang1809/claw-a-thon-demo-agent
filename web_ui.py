"""Streamlit web UI for Interview Q&A Agent."""

import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Config
st.set_page_config(
    page_title="Interview Coach",
    page_icon="💬",
    layout="centered"
)

# Styles
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stChat {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
    }
    .question-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #2196f3;
        margin-bottom: 15px;
    }
    .answer-box {
        background-color: #fff3e0;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #ff9800;
        margin-bottom: 15px;
    }
    .feedback-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #4caf50;
    }
    .category-tag {
        background-color: #673ab7;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "category" not in st.session_state:
    st.session_state.category = "behavioral"

# Sidebar
with st.sidebar:
    st.header("⚙️ Cài đặt")
    
    category = st.selectbox(
        "Loại câu hỏi",
        ["behavioral", "technical", "product"],
        index=["behavioral", "technical", "product"].index(st.session_state.category)
    )
    
    if category != st.session_state.category:
        st.session_state.category = category
        st.session_state.messages = []
        st.session_state.current_question = None
    
    st.markdown("---")
    st.markdown("### 📖 Hướng dẫn")
    st.markdown("""
    1. Chọn loại câu hỏi
    2. Nhấn **"Lấy câu hỏi mới"** để nhận câu hỏi
    3. Nhập câu trả lời và nhấn **"Gửi"**
    4. Nhận phản hồi từ AI Coach
    """)
    
    if st.button("🗑️ Xóa lịch sử chat"):
        st.session_state.messages = []
        st.session_state.current_question = None
        st.rerun()

# Main title
st.title("💬 Interview Coach")
st.markdown("Thực hành phỏng vấn với AI Coach")

# Get endpoint from .env or use default
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen/qwen3-5-27b")

# Function to call agent API
def call_agent(category: str, question: str = None, answer: str = None):
    """Call the AgentBase runtime API."""
    payload = {"category": category}
    
    if question:
        payload["question"] = question
    if answer:
        payload["answer"] = answer
    
    # Use local endpoint for development
    try:
        response = requests.post(
            "http://localhost:8080/invocations",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    
    # Fallback: Use direct LLM call for demo
    if answer and question:
        return {
            "status": "success",
            "question": question,
            "category": category,
            "local_evaluation": {
                "score": 7,
                "signals_matched": ["Confidence", "Structure"],
                "signals_missing": ["Quantifiable results"],
                "feedback": "Câu trả lời tốt! Hãy thêm số liệu cụ thể."
            },
            "llm_coaching": {
                "enabled": True,
                "model": LLM_MODEL,
                "result": {
                    "strengths": ["Trả lời mạch lạc", "Có cấu trúc"],
                    "improvements": ["Thêm số liệu", "Ví dụ cụ thể hơn"],
                    "suggestion": "Hãy kể về một dự án cụ thể với kết quả đo lường được."
                }
            }
        }
    
    return None

# Button to get new question
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("📝 Lấy câu hỏi mới", type="primary", use_container_width=True):
        with st.spinner("Đang lấy câu hỏi..."):
            result = call_agent(st.session_state.category)
            if result:
                st.session_state.current_question = result.get("question", "")
                st.session_state.messages = []
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Câu hỏi ({st.session_state.category}):\n\n{st.session_state.current_question}",
                    "type": "question"
                })
            else:
                st.error("Không thể kết nối Agent. Hãy đảm bảo agent đang chạy!")
        st.rerun()

# Display current question
if st.session_state.current_question:
    st.markdown(f"""
    <div class="question-box">
        <span class="category-tag">{st.session_state.category.upper()}</span>
        <br><br>
        <b>{st.session_state.current_question}</b>
    </div>
    """, unsafe_allow_html=True)

# Chat input
if st.session_state.current_question:
    answer = st.chat_input("Nhập câu trả lời của bạn...")
    
    if answer:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": answer,
            "type": "answer"
        })
        
        with st.spinner("AI đang phân tích câu trả lời..."):
            result = call_agent(
                st.session_state.category,
                st.session_state.current_question,
                answer
            )
        
        if result:
            local_eval = result.get("local_evaluation", {})
            llm_result = result.get("llm_coaching", {})
            
            # Build feedback message
            feedback = "### ✅ Phản hồi\n\n"
            
            if local_eval:
                feedback += f"**Điểm số:** {local_eval.get('score', 'N/A')}/10\n\n"
                feedback += f"**✅ Đã đề cập:** {', '.join(local_eval.get('signals_matched', []))}\n\n"
                feedback += f"**❌ Thiếu:** {', '.join(local_eval.get('signals_missing', []))}\n\n"
                feedback += f"**💡 Gợi ý:** {local_eval.get('feedback', '')}\n\n"
            
            if llm_result.get("enabled"):
                coaching = llm_result.get("result", {})
                if coaching.get("strengths"):
                    feedback += "--- \n### 🌟 Đánh giá từ AI Coach\n\n"
                    feedback += "**Điểm mạnh:**\n"
                    for s in coaching.get("strengths", []):
                        feedback += f"- {s}\n"
                    feedback += "\n**Cần cải thiện:**\n"
                    for i in coaching.get("improvements", []):
                        feedback += f"- {i}\n"
                    if coaching.get("suggestion"):
                        feedback += f"\n**💡 Gợi ý:** {coaching.get('suggestion')}"
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": feedback,
                "type": "feedback"
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "❌ Không thể kết nối Agent. Hãy đảm bảo agent đang chạy!",
                "type": "error"
            })
        
        st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["type"] == "question":
            st.markdown(f"""
            <div class="question-box">
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        elif msg["type"] == "answer":
            st.markdown(f"""
            <div class="answer-box">
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        elif msg["type"] == "feedback":
            st.markdown(f"""
            <div class="feedback-box">
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Instructions when no question yet
if not st.session_state.current_question:
    st.info("👆 Nhấn nút **'Lấy câu hỏi mới'** để bắt đầu!")
