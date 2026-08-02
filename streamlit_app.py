import streamlit as st

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Egyptian Civil Status AI",
    page_icon="🏛️",
    layout="centered"
)

# =========================================================
# EMBEDDED CSS (لضمان وضوح جميع النصوص والأجزاء)
# =========================================================

st.markdown(
    """
    <style>
    /* فرض لون داكن وواضح لكل النصوص في الصفحة */
    p, span, label, .stMarkdown, .stSubheader, h3 {
        color: #1a202c !important;
    }
    /* ضمان وضوح عناوين الخدمات */
    div[data-testid="column"] p {
        color: #1a202c !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 40px; border-radius: 20px; text-align: center; color: white; margin-bottom: 20px;">
        <h1 style="color: white; margin-bottom: 10px;">🏛️ Egyptian Civil Status AI</h1>
        <p style="font-size: 16px; margin: 5px 0; color: #e2e8f0;">Smart Assistant for Egyptian Civil Status Services</p>
        <p style="font-size: 14px; margin: 0; color: #cbd5e1;">Powered by RAG • OpenRouter • Artificial Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# =========================================================
# QUESTION
# =========================================================

st.subheader("💬 Ask Your Question")

question = st.text_input(
    "Ask about Egyptian Civil Status Services",
    placeholder="Example: What documents are required for a National ID?"
)

if st.button("🚀 Ask Assistant", use_container_width=False):

    if question.strip():

        st.info("🔎 Searching the government knowledge base...")

        st.write("**Your Question:**")
        st.write(question)

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

            st.markdown(
                f"""
                **{icon} {title}**

                {description}
                """
            )

            st.write("")

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🇪🇬 Egyptian Civil Status AI • RAG-Based Government Services Assistant"
)
