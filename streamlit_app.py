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

# 3. Cache Resource to save memory (RAM)
@st.cache_data(show_spinner=False)
def get_answer(query: str):
    return prompting_module.answer_question(query)


# 4. Custom Styling (CSS)
st.markdown("""
<style>
    /* Main Header */
    .header-box {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        padding: 35px 20px;
        border-radius: 18px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(30, 64, 175, 0.2);
    }
    .header-box h1 {
        color: white !important;
        font-size: 2.3rem !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
    }
    .header-box p {
        color: #e0e7ff !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
    }
    .header-icon {
        font-size: 45px;
        margin-bottom: 10px;
    }

    /* Sub-headers */
    .sub-title {
        text-align: center;
        color: #1e3a8a;
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 20px;
    }

    /* Cards styling */
    div.stButton > button {
        width: 100%;
        height: 110px;
        background-color: #ffffff;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        white-space: pre-wrap;
    }
    div.stButton > button:hover {
        border-color: #3b82f6;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.15);
        transform: translateY(-3px);
        background-color: #f8fafc;
    }
    
    /* Result Box */
    .result-container {
        background-color: #ffffff;
        border-left: 5px solid #3b82f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 5. UI Header Rendering
st.markdown("""
<div class="header-box">
    <div class="header-icon">🏛️</div>
    <h1>Egyptian Civil Status AI</h1>
    <p>Smart Assistant for Egyptian Civil Status Services<br>Powered by RAG • OpenRouter • Artificial Intelligence</p>
</div>
""", unsafe_allow_html=True)

# 6. Ask Question Section
st.markdown('<div class="sub-title">💬 Ask Your Question</div>', unsafe_allow_html=True)

# Session state initialization for dynamic query
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

# 7. Popular Services Buttons
st.markdown('<div class="sub-title">✨ Popular Services</div>', unsafe_allow_html=True)

row1_col1, row1_col2, row1_col3 = st.columns(3)
row2_col1, row2_col2, row2_col3 = st.columns(3)

clicked_query = None

with row1_col1:
    if st.button("🪪\n\nNational ID\nIssue or Renew National ID"):
        clicked_query = "ما هي شروط وإجراءات استخراج أو تجديد بطاقة الرقم القومي؟"

with row1_col2:
    if st.button("👶\n\nBirth Certificate\nIssue Birth Certificate"):
        clicked_query = "ما هي الأوراق والشروط المطلوبة لاستخراج شهادة الميلاد؟"

with row1_col3:
    if st.button("💍\n\nMarriage Certificate\nMarriage Registration"):
        clicked_query = "ما هي إجراءات وشروط توثيق أو استخراج وثيقة الزواج؟"

with row2_col1:
    if st.button("👨‍👩‍👧‍👦\n\nFamily Record\nIssue Family Record"):
        clicked_query = "ما هي مستندات وشروط استخراج القيد العائلي لأول مرة؟"

with row2_col2:
    if st.button("⚰️\n\nDeath Certificate\nIssue Death Certificate"):
        clicked_query = "ما هي خطوات وإجراءات استخراج شهادة الوفاة؟"

with row2_col3:
    if st.button("🏠\n\nAddress Update\nUpdate Address"):
        clicked_query = "كيف يمكن تغيير أو تحديث محل الإقامة في بطاقة الرقم القومي؟"

# 8. Execution Logic
query_to_run = clicked_query or (user_input if ask_button and user_input.strip() else None)

if query_to_run:
    st.markdown("---")
    with st.spinner("جاري البحث في المستندات والإجابة..."):
        try:
            res = get_answer(query_to_run)
            answer_text = res.get("answer", "")
            sources = res.get("sources", [])

            # Check if context was not enough
            not_enough_info_triggers = [
                "غير كاف", "لا يوجد", "لم يتم العثور", "غير متوفر",
                "لا تحتوي المستندات", "لا توجد معلومات"
            ]
            is_insufficient = any(trigger in answer_text for trigger in not_enough_info_triggers)

            st.markdown("### 📝 الإجابة:")
            st.info(answer_text)

            # ONLY show sources if information is available and grounded
            if sources and not is_insufficient:
                st.markdown("### 📚 المصادر المعتمدة:")
                for src in sources:
                    st.success(f"📌 {src}")
            elif is_insufficient:
                st.warning("⚠️ لم يتم عرض المصادر لأن المعلومات غير متوفرة في قاعدة البيانات.")

        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة الطلب: {e}")
