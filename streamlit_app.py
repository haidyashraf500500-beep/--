# -*- coding: utf-8 -*-
"""
streamlit_app.py
================
Streamlit UI for Egyptian Civil Status AI Assistant (RAG Pipeline)
"""

import importlib.util
import os
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Egyptian Civil Status AI",
    page_icon="🏛️",
    layout="centered"
)

# 2. Dynamic Module Loader
def _load_module(filename: str, alias: str):
    module_path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(alias, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load Prompting Stage
prompting_module = _load_module("07_prompting.py", "stage07_prompting")

# Handle OpenRouter API Key securely from Streamlit Secrets
if "OPENROUTER_API_KEY" in st.secrets:
    prompting_module.OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# 3. Cache Resource to save memory
@st.cache_data(show_spinner=False)
def get_answer(query: str):
    return prompting_module.answer_question(query)

# 4. Custom Styling (Advanced CSS for Stunning UI)
st.markdown("""
<style>
    /* Main Header Container */
    .header-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: #ffffff;
        padding: 40px 20px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.3);
    }
    .header-box h1 {
        color: #ffffff !important;
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        margin-bottom: 10px !important;
        letter-spacing: -0.5px;
    }
    .header-box p {
        color: #e0e7ff !important;
        font-size: 1rem !important;
        margin: 0 !important;
        font-weight: 400;
    }
    .header-icon {
        font-size: 50px;
        margin-bottom: 12px;
    }

    /* Section Subtitles */
    .section-title {
        text-align: center;
        color: #3b82f6;
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 15px;
        letter-spacing: 0.3px;
    }

    /* Professional Cards Styling */
    div.stButton > button {
        width: 100%;
        height: 120px;
        background: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        white-space: pre-wrap;
        font-weight: 600;
    }
    div.stButton > button:hover {
        border-color: #3b82f6 !important;
        background: #0f172a !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
        transform: translateY(-4px);
    }

    /* Primary Action Button (Ask Assistant) */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
        color: white !important;
        height: 50px !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
    }
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# 5. UI Header Rendering
st.markdown("""
<div class="header-box">
    <div class="header-icon">🏛️</div>
    <h1>Egyptian Civil Status AI</h1>
    <p>مساعد رقمي ذكي لخدمات الأحوال المدنية المصرية<br>Powered by RAG • OpenRouter • Artificial Intelligence</p>
</div>
""", unsafe_allow_html=True)

# 6. Ask Question Section
st.markdown('<div class="section-title">💬 Ask Your Question / اسأل سؤالك</div>', unsafe_allow_html=True)

if "user_query" not in st.session_state:
    st.session_state["user_query"] = ""

user_input = st.text_input(
    label="Search Box",
    placeholder="اكتب سؤالك هنا (مثال: ما هي الأوراق المطلوبة لاستخراج بطاقة رقم قومي؟)...",
    value=st.session_state["user_query"],
    label_visibility="collapsed"
)

col_center = st.columns([1, 2, 1])
with col_center[1]:
    ask_button = st.button("🚀 Ask Assistant", use_container_width=True, type="primary")

# 7. Popular Services Quick Cards
st.markdown('<div class="section-title">✨ Popular Services / الخدمات الشائعة</div>', unsafe_allow_html=True)

row1_col1, row1_col2, row1_col3 = st.columns(3)
row2_col1, row2_col2, row2_col3 = st.columns(3)

clicked_query = None

with row1_col1:
    if st.button("🪪\n\nNational ID\nبطاقة الرقم القومي"):
        clicked_query = "ما هي شروط وإجراءات استخراج أو تجديد بطاقة الرقم القومي؟"

with row1_col2:
    if st.button("👶\n\nBirth Certificate\nشهادة الميلاد"):
        clicked_query = "ما هي الأوراق والشروط المطلوبة لاستخراج شهادة الميلاد؟"

with row1_col3:
    if st.button("💍\n\nMarriage Certificate\nوثيقة الزواج"):
        clicked_query = "ما هي إجراءات وشروط توثيق أو استخراج وثيقة الزواج؟"

with row2_col1:
    if st.button("👨‍👩‍👧‍👦\n\nFamily Record\nالقيد العائلي"):
        clicked_query = "ما هي مستندات وشروط استخراج القيد العائلي لأول مرة؟"

with row2_col2:
    if st.button("⚰️\n\nDeath Certificate\nشهادة الوفاة"):
        clicked_query = "ما هي خطوات وإجراءات استخراج شهادة الوفاة؟"

with row2_col3:
    if st.button("🏠\n\nAddress Update\nتحديث محل الإقامة"):
        clicked_query = "كيف يمكن تغيير أو تحديث محل الإقامة في بطاقة الرقم القومي؟"

# 8. Execution Logic & Response Filtering
query_to_run = clicked_query or (user_input if ask_button and user_input.strip() else None)

if query_to_run:
    st.markdown("---")
    with st.spinner("جاري البحث والتحليل في المستندات الحكومية..."):
        try:
            res = get_answer(query_to_run)
            answer_text = res.get("answer", "")
            sources = res.get("sources", [])

            # Check if context was insufficient (No Hallucination Handling)
            not_enough_info_triggers = [
                "غير كاف", "لا يوجد", "لم يتم العثور", "غير متوفر",
                "لا تحتوي المستندات", "لا توجد معلومات", "عفواً"
            ]
            is_insufficient = any(trigger in answer_text for trigger in not_enough_info_triggers)

            st.markdown("### 📝 الإجابة الرسمية:")
            st.info(answer_text)

            # STRICT RULE: ONLY show sources if information is valid and sufficient
            if sources and not is_insufficient:
                st.markdown("### 📚 المصادر المعتمدة:")
                for src in sources:
                    st.success(f"📌 {src}")
            elif is_insufficient:
                # Completely skip showing sources when info is missing
                pass

        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة الطلب: {e}")
