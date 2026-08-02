import streamlit as st
import os
import importlib.util

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Egyptian Civil Status AI",
    page_icon="🏛️",
    layout="centered"
)

# =========================================================
# LOAD 07_PROMPTING MODULE & API KEY
# =========================================================

def load_prompting_module():
    try:
        module_path = os.path.join(os.path.dirname(__file__), "07_prompting.py")
        spec = importlib.util.spec_from_file_location("stage07_prompting", module_path)
        prompting_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(prompting_mod)
        return prompting_mod
    except Exception as e:
        return None

prompting = load_prompting_module()

# جلب مفتاح OpenRouter بأمان (سواء محلياً من .env أو عبر secrets إن وجدت)
api_key = os.getenv("OPENROUTER_API_KEY", "")
try:
    if "OPENROUTER_API_KEY" in st.secrets:
        api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    pass  # تخطي الخطأ إذا لم يكن ملف secrets.toml موجوداً محلياً

if api_key and prompting:
    prompting.OPENROUTER_API_KEY = api_key

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    p, span, label, .stMarkdown, .stSubheader {
        color: #f3f4f6 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HERO SECTION
# =========================================================

st.markdown(
    """
    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 40px; border-radius: 20px; text-align: center; color: white; margin-bottom: 20px;">
        <h1 style="color: white; margin-bottom: 10px;">🏛️ Egyptian Civil Status AI</h1>
        <p style="font-size: 16px; margin: 5px 0; color: #f8fafc;">Smart Assistant for Egyptian Civil Status Services</p>
        <p style="font-size: 14px; margin: 0; color: #e2e8f0;">Powered by RAG • OpenRouter • Artificial Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# =========================================================
# QUESTION SECTION & RAG INTEGRATION
# =========================================================

st.subheader("💬 Ask Your Question")

question = st.text_input(
    "Ask about Egyptian Civil Status Services",
    placeholder="Example: What documents are required for a National ID?"
)

if st.button("🚀 Ask Assistant", use_container_width=False):
    if question.strip():
        if prompting is None:
            st.error("تعذر تحميل ملف 07_prompting.py. تأكد من وجوده في نفس مجلد المشروع.")
        else:
            with st.spinner("🔎 جاري البحث في قاعدة المعارف الحكومية وتوليد الإجابة..."):
                try:
                    result = prompting.answer_question(question)
                    
                    st.success("تم إتمام البحث بنجاح:")
                    st.markdown("### الإجابة:")
                    st.write(result["answer"])
                    
                    if result.get("sources"):
                        st.markdown("---")
                        st.markdown("**المصادر المعتمدة:**")
                        for src in result["sources"]:
                            st.markdown(f"- {src}")
                            
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال بنظام الـ RAG أو OpenRouter: {e}")
    else:
        st.warning("Please enter your question first.")

# =========================================================
# POPULAR SERVICES
# =========================================================

st.subheader("✨ Popular Services")

services = [
    ("🪪", "National ID", "Issue or Renew National ID"),
    ("👶", "Birth Certificate", "Issue Birth Certificate"),
    ("💍", "Marriage Certificate", "Marriage Registration"),
    ("👨‍👩‍👧", "Family Record", "Issue Family Record"),
    ("🏷️", "Death Certificate", "Issue Death Certificate"),
    ("🏠", "Address Update", "Update Address")
]

for i in range(0, 6, 3):
    cols = st.columns(3)
    for col, service in zip(cols, services[i:i + 3]):
        icon, title, description = service
        with col:
            if st.button(f"{icon} {title}\n\n{description}", use_container_width=True):
                if prompting:
                    with st.spinner(f"جاري البحث عن خدمة: {title}..."):
                        try:
                            res = prompting.answer_question(f"ما هي إجراءات وشروط {title}؟")
                            st.success(f"إجابة خدمة {title}:")
                            st.write(res["answer"])
                        except Exception as e:
                            st.error(f"خطأ: {e}")
                else:
                    st.error("ملف الـ RAG غير محمل.")

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🇪🇬 Egyptian Civil Status AI • RAG-Based Government Services Assistant"
)
