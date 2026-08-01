# -*- coding: utf-8 -*-

import streamlit as st
import importlib.util
import os

# =====================================================
# Load RAG Module
# =====================================================

def _load_module(filename: str, alias: str):
    module_path = os.path.join(os.path.dirname(__file__), filename)

    spec = importlib.util.spec_from_file_location(
        alias,
        module_path
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


rag = _load_module(
    "07_prompting.py",
    "stage07_prompting"
)

# =====================================================
# Read Secrets
# =====================================================

try:

    if not rag.OPENROUTER_API_KEY:

        rag.OPENROUTER_API_KEY = st.secrets.get(
            "OPENROUTER_API_KEY",
            ""
        )

    rag.OPENROUTER_MODEL = st.secrets.get(
        "OPENROUTER_MODEL",
        rag.OPENROUTER_MODEL
    )

except Exception:
    pass

# =====================================================
# Page Config
# =====================================================

st.set_page_config(
    page_title="Egyptian Civil Status AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# Custom CSS (Professional Styling)
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"]{
    font-family: 'Poppins', sans-serif;
}

header{
    visibility: hidden;
}

#MainMenu{
    visibility: hidden;
}

footer{
    visibility: hidden;
}

.stApp{
    background: linear-gradient(135deg, #F4F8FF, #EEF5FF);
}

.block-container{
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero{
    background: linear-gradient(135deg, #0F4C81, #2563EB);
    border-radius: 25px;
    padding: 45px;
    text-align: center;
    color: white;
    box-shadow: 0 15px 40px rgba(0,0,0,.15);
    margin-bottom: 35px;
}

.hero h1{
    font-size: 48px;
    margin-bottom: 12px;
    color: white !important;
}

.hero p{
    font-size: 20px;
    opacity: .95;
    color: white !important;
}

.service-card{
    background: white;
    border-radius: 18px;
    padding: 22px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(0,0,0,.08);
    border: 1px solid #E5E7EB;
    transition: .3s;
    margin-bottom: 20px;
    color: #111827 !important;
}

.service-card:hover{
    transform: translateY(-6px);
}

.answer-card{
    background: white;
    border-radius: 18px;
    padding: 25px;
    box-shadow: 0 8px 25px rgba(0,0,0,.08);
    border-left: 6px solid #2563EB;
    margin-top: 20px;
    color: #111827 !important;
}

.answer-card p, .answer-card span, .answer-card div, .answer-card li {
    color: #111827 !important;
}

.service-card p, .service-card span, .service-card div {
    color: #111827 !important;
}

.stTextInput input{
    background: white !important;
    color: #111827 !important;
    border: 2px solid #D6E4FF !important;
    border-radius: 16px !important;
    padding: 14px !important;
    font-size: 17px !important;
}

.stTextInput input:focus{
    border: 2px solid #2563EB !important;
    box-shadow: 0 0 0 4px rgba(37,99,235,.15) !important;
}

/* Professional Modern Button Styling */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #0F4C81, #2563EB) !important;
    color: white !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    border-radius: 16px !important;
    border: none !important;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 25px rgba(37, 99, 235, 0.35) !important;
    background: linear-gradient(135deg, #0c3d68, #1d4ed8) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# Hero Section
# =====================================================

st.markdown("""
<div class="hero">
<div style="font-size:80px;">🏛️</div>
<h1>Egyptian Civil Status AI</h1>
<p>
Smart Assistant for Egyptian Civil Status Services<br>
Powered by RAG • OpenRouter • Artificial Intelligence
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# Search
# =====================================================

st.markdown("""
<h2 style="text-align:center;color:#0F4C81;">
💬 Ask Your Question
</h2>
""", unsafe_allow_html=True)

query = st.text_input(
    "",
    placeholder="Example: How can I renew my National ID?"
)

col1, col2, col3 = st.columns([1,2,1])

with col2:
    ask_clicked = st.button("🚀 Ask Assistant", key="ask_button")

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# Popular Services
# =====================================================

st.markdown("""
<h2 style="text-align:center;color:#0F4C81;">
✨ Popular Services
</h2>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="service-card">
        <div style="font-size:35px; margin-bottom:8px;">🪪</div>
        <div style="font-size:18px; font-weight:600; color:#0F4C81;">National ID</div>
        <div style="font-size:14px; color:#6B7280; margin-top:5px;">Issue or Renew National ID</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="service-card">
        <div style="font-size:35px; margin-bottom:8px;">👶</div>
        <div style="font-size:18px; font-weight:600; color:#0F4C81;">Birth Certificate</div>
        <div style="font-size:14px; color:#6B7280; margin-top:5px;">Issue Birth Certificate</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="service-card">
        <div style="font-size:35px; margin-bottom:8px;">💍</div>
        <div style="font-size:18px; font-weight:600; color:#0F4C81;">Marriage Certificate</div>
        <div style="font-size:14px; color:#6B7280; margin-top:5px;">Marriage Registration</div>
    </div>
    """, unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)

with c4:
    st.markdown("""
    <div class="service-card">
        <div style="font-size:35px; margin-bottom:8px;">👨‍👩‍👧</div>
        <div style="font-size:18px; font-weight:600; color:#0F4C81;">Family Record</div>
        <div style="font-size:14px; color:#6B7280; margin-top:5px;">Issue Family Record</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown("""
    <div class="service-card">
        <div style="font-size:35px; margin-bottom:8px;">⚰️</div>
        <div style="font-size:18px; font-weight:600; color:#0F4C81;">Death Certificate</div>
        <div style="font-size:14px; color:#6B7280; margin-top:5px;">Issue Death Certificate</div>
    </div>
    """, unsafe_allow_html=True)

with c6:
    st.markdown("""
    <div class="service-card">
        <div style="font-size:35px; margin-bottom:8px;">🏠</div>
        <div style="font-size:18px; font-weight:600; color:#0F4C81;">Address Update</div>
        <div style="font-size:14px; color:#6B7280; margin-top:5px;">Update Address</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# Execute Question
# =====================================================

if ask_clicked:

    st.markdown(
        """
        <div style="
            background: white;
            color: #111827;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            font-weight: 500;
        ">
        ✅ Button clicked
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="
            background: white;
            color: #111827;
            padding: 15px;
            border-radius: 10px;
            font-weight: 500;
        ">
        Question: {query}
        </div>
        """,
        unsafe_allow_html=True
    )

    if query.strip() == "":
        st.warning("Please enter your question.")
    else:
        with st.spinner("Searching Knowledge Base..."):
            result = rag.answer_question(
                query=query,
                k=6,
                word_budget=220,
                max_chunks=4
            )

                 st.markdown(
            f"""
            <div class="answer-card">
            {result["answer"]}
            </div>
            """,
            unsafe_allow_html=True
        )

        # اعرض المصادر فقط إذا كانت موجودة
        if result["sources"]:

            st.markdown("## 📚 Sources")

            for source in result["sources"]:
                st.markdown(
                    f"""
                    <div class="service-card">
                    📄 {source}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
