# -*- coding: utf-8 -*-
"""
streamlit_app.py
=================
Final stage: Streamlit UI.

documents -> preprocessing -> chunking -> vector representation -> vector store
-> context retrieval -> prompting -> [Streamlit UI]

Loads `rag` = 07_prompting.py (which in turn loads every earlier stage) and
exposes a simple chat-style assistant over the civil-status document.

Streamlit secrets: on Streamlit Cloud, add OPENROUTER_API_KEY and
OPENROUTER_MODEL in the app's Secrets panel (TOML format). This file reads
them from `st.secrets` and injects them into the `rag` module at runtime, so
no real key is ever written into a tracked file.
"""

import importlib.util
import os

import streamlit as st


def _load_module(filename: str, alias: str):
    module_path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(alias, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rag = _load_module("07_prompting.py", "stage07_prompting")

# --- Wire up Streamlit secrets (deployed) without touching real keys here ---
try:
    if not rag.OPENROUTER_API_KEY:
        rag.OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    rag.OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", rag.OPENROUTER_MODEL)
except Exception:
    # st.secrets raises if no secrets.toml exists (e.g. running purely locally
    # with a .env file instead) - that is fine, just keep the env-based values.
    pass


st.set_page_config(page_title="مساعد الأحوال المدنية", page_icon="🗂️", layout="centered")

st.title("🗂️ مساعد الأحوال المدنية")
st.caption(
    "نظام RAG يجيب فقط بالاعتماد على دليل مستندات وإجراءات الأحوال المدنية المصري "
    "(بطاقة الرقم القومي، شهادات الميلاد والوفاة، قسائم الزواج والطلاق، القيد العائلي، "
    "جواز السفر، رخصة القيادة، الشهر العقاري، التموين والفيش)."
)

if not rag.OPENROUTER_API_KEY:
    st.warning(
        "لم يتم العثور على OPENROUTER_API_KEY. أضفه في ملف `.env` محلياً "
        "أو في Streamlit Secrets عند النشر (راجع README.md)."
    )

with st.sidebar:
    st.header("الإعدادات")
    top_k = st.slider("عدد الـ chunks المسترجعة (k)", min_value=2, max_value=10, value=6)
    max_chunks = st.slider("أقصى عدد chunks في السياق النهائي", min_value=1, max_value=6, value=4)
    word_budget = st.slider("ميزانية الكلمات في السياق", min_value=80, max_value=400, value=220, step=20)
    st.markdown("---")
    st.caption(f"النموذج الحالي: `{rag.OPENROUTER_MODEL}`")

query = st.text_input(
    "اكتب سؤالك",
    placeholder="مثال: كام سعر استخراج بطاقة الرقم القومي بالفئة الفورية؟",
)

ask_clicked = st.button("اسأل", type="primary")

if ask_clicked and query.strip():
    with st.spinner("جاري البحث عن الأدلة وتوليد الإجابة..."):
        result = rag.answer_question(
            query,
            k=top_k,
            word_budget=word_budget,
            max_chunks=max_chunks,
         )

    st.subheader("الإجابة")
    st.write(result["answer"])

    st.subheader("المصادر المستخدمة")
    if result["sources"]:
        for source in result["sources"]:
            st.markdown(f"- {source}")
    else:
        st.info("لم يتم العثور على مصادر ذات صلة كافية بهذا السؤال.")

    with st.expander("عرض السياق الذي اعتمدت عليه الإجابة (Debug)"):
        st.text(result["context_text"])

elif ask_clicked:
    st.info("من فضلك اكتب سؤالاً أولاً.")
