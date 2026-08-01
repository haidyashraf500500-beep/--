# -*- coding: utf-8 -*-
"""
07_prompting.py
================
Stage 7 of the pipeline: prompting.

documents -> preprocessing -> chunking -> vector representation -> vector store
-> context retrieval -> [prompting] -> Streamlit UI

Loads `build_context_package` from 06_retrieve_context.py, builds a grounded
Arabic prompt, and calls an LLM through the OpenRouter API. This is the ONLY
file that talks to an external LLM API.

API key handling:
- Locally: set OPENROUTER_API_KEY in a `.env` file (never commit it) and load
  it with python-dotenv, OR export it as an environment variable.
- On Streamlit Cloud: leave OPENROUTER_API_KEY unset here. streamlit_app.py
  reads it from `st.secrets` and assigns it to this module at runtime -
  see the `OPENROUTER_API_KEY = ...` line below and streamlit_app.py.
"""

import importlib.util
import os

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv is optional; on Streamlit Cloud secrets are used instead.
    pass


def _load_module(filename: str, alias: str):
    module_path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(alias, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_retrieval_module = _load_module("06_retrieve_context.py", "stage06_retrieve_context")
build_context_package = _retrieval_module.build_context_package

# --- API configuration -------------------------------------------------
# NEVER hard-code a real key here. This just reads from the environment
# (locally) and is overwritten from st.secrets when deployed on Streamlit.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def build_grounded_prompt(query: str, context_text: str) -> str:
    return f"""
أنت مساعد ذكي متخصص في خدمات الأحوال المدنية المصرية.

مهمتك الإجابة عن أسئلة المستخدم اعتماداً على السياق المرفق.

القواعد:
- استخدم المعلومات الموجودة في السياق كأولوية.
- إذا كانت الإجابة موجودة في السياق، قدمها بشكل واضح ومنظم.
- لا تخترع أسعار أو أرقام أو قوانين غير موجودة.
- إذا لم تجد معلومات كافية للإجابة، قل:
"لا أملك معلومات كافية في المستندات المتاحة للإجابة على هذا السؤال."
- لا ترفض الإجابة لمجرد أن السياق مختصر، حاول الاستفادة من المعلومات المتاحة.
- أجب باللغة العربية البسيطة.
- في نهاية الإجابة اذكر المصادر التي اعتمدت عليها فقط إذا كانت موجودة.

السؤال:
{query}

السياق:
{context_text}
"""
def call_openrouter(prompt: str, model: str = None, temperature: float = 0.0) -> str:
    model = model or OPENROUTER_MODEL

    if not OPENROUTER_API_KEY:
        return (
            "لا يوجد مفتاح OPENROUTER_API_KEY متاح. أضفه في ملف .env محلياً، "
            "أو في Streamlit secrets عند النشر."
        )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except Exception as exc:
        return f"OpenRouter request failed: {exc}"

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError):
        return f"Unexpected OpenRouter response: {data}"


def answer_question(query: str, k: int = 6, word_budget: int = 220, max_chunks: int = 4) -> dict:
    """Full retrieval -> prompt -> generation flow for one user question."""
    package = build_context_package(query, k=k, word_budget=word_budget, max_chunks=max_chunks)
    prompt = build_grounded_prompt(package["query"], package["context_text"])
    answer_text = call_openrouter(prompt)

    return {
        "query": query,
        "answer": answer_text,
        "sources": package["sources"],
        "context_text": package["context_text"],
        "prompt": prompt,
    }


def main() -> None:
    demo_query = "عايز أسجل شقة مساحتها 150 متر في الشهر العقاري، الرسوم كام؟"
    result = answer_question(demo_query)

    print(f"Query: {result['query']}\n")
    print("Sources:")
    for source in result["sources"]:
        print(f"  - {source}")
    print("\nAnswer:")
    print(result["answer"])


if __name__ == "__main__":
    main()
