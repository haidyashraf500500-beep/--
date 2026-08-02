# -*- coding: utf-8 -*-
"""
streamlit_app.py
================
Streamlit UI for Egyptian Civil Status AI Assistant (Lightweight & Low Memory)
"""

import os
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Egyptian Civil Status AI",
    page_icon="🏛️",
    layout="centered"
)

# 2. Lazy Import Function for Prompting Stage (Saves RAM)
@st.cache_resource(show_spinner=False)
def get_answer_function():
    import importlib.util
    module_path = os.path.join(os.path.dirname(__file__), "07_prompting.py")
    spec = importlib.util.spec_from_file_location("stage07_prompting", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if "OPENROUTER_API_KEY" in st.secrets:
        module.OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
        
    return module.answer_question

# 3. Custom Styling (Stunning UI & Fixed Colors)
st.markdown("""
<style>
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
    }
    .header-box p {
        color: #e0e7ff !important;
        font-size: 1rem !important;
        margin: 0 !important;
    }
    .section-title {
        text-align: center;
        color: #3b82f6;
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    div.stButton > button {
        width: 100%;
        height: 110px;
        background: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
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
        transform: translateY(-3px);
    }
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
        color: white !important;
        height: 50px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. UI Header Rendering
st.markdown("""
<div class="header-box">
    <div style="font-size: 50px; margin-bottom: 12px;">🏛️</div>
    <h1>Egyptian Civil Status AI</h1>
    <p>مساعد رقمي ذكي لخدمات الأحوال المدنية المصرية<br>Powered by RAG • OpenRouter • Artificial Intelligence</p>
</div>
""", unsafe_allow_html=True)

# 5. Search Bar Section
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

# 6. Popular Services Quick Cards
st.markdown('<div class="section-title">✨ Popular Services / الخدمات الشائعة</div>', unsafe_allow_html=True)

r1_c1, r1_c2, r1_c3 = st.columns(3)
r2_c1, r2_c2, r2_c3 = st.columns(3)

clicked_query = None

with r1_c1:
    if st.button("🪪\n\nNational ID\nبطاقة الرقم القومي"):
        clicked_query = "ما هي شروط وإجراءات استخراج أو تجديد بطاقة الرقم القومي؟"
with r1_c2:
    if st.button("👶\n\nBirth Certificate\nشهادة الميلاد"):
        clicked_query = "ما هي الأوراق والشروط المطلوبة لاستخراج شهادة الميلاد؟"
with r1_c3:
    if st.button("💍\n\nMarriage Certificate\nوثيقة الزواج"):
        clicked_query = "ما هي إجراءات وشروط توثيق أو استخراج وثيقة الزواج؟"
with r2_c1:
    if st.button("👨‍👩‍👧‍👦\n\nFamily Record\nالقيد العائلي"):
        clicked_query = "ما هي مستندات وشروط استخراج القيد العائلي لأول مرة؟"
with r2_c2:
    if st.button("⚰️\n\nDeath Certificate\nشهادة الوفاة"):
        clicked_query = "ما هي خطوات وإجراءات استخراج شهادة الوفاة؟"
with r2_c3:
    if st.button("🏠\n\nAddress Update\nتحديث محل الإقامة"):
        clicked_query = "كيف يمكن تغيير أو تحديث محل الإقامة في بطاقة الرقم القومي؟"

# 7. Execution Logic
query_to_run = clicked_query or (user_input if ask_button and user_input.strip() else None)

if query_to_run:
    st.markdown("---")
    with st.spinner("جاري البحث والتحليل في المستندات الحكومية..."):
        try:
            answer_func = get_answer_function()
            res = answer_func(query_to_run)
            answer_text = res.get("answer", "")
            sources = res.get("sources", [])

            not_enough_info_triggers = [
                "غير كاف", "لا يوجد", "لم يتم العثور", "غير متوفر",
                "لا تحتوي المستندات", "لا توجد معلومات", "عفواً"
            ]
            is_insufficient = any(trigger in answer_text for trigger in not_enough_info_triggers)

            st.markdown("### 📝 الإجابة الرسمية:")
            st.info(answer_text)

            if sources and not is_insufficient:
                st.markdown("### 📚 المصادر المعتمدة:")
                for src in sources:
                    st.success(f"📌 {src}")
            elif is_insufficient:
                pass

        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة الطلب: {e}")
