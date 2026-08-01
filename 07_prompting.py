# -*- coding: utf-8 -*-

import importlib.util
import os
import requests


def _load_module(filename: str, alias: str):
    module_path = os.path.join(os.path.dirname(__file__), filename)

    spec = importlib.util.spec_from_file_location(
        alias,
        module_path
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


# ==============================
# Load Retrieval Stage
# ==============================

_retrieval_module = _load_module(
    "06_retrieve_context.py",
    "stage06_retrieve_context"
)

build_context_package = _retrieval_module.build_context_package


# ==============================
# OpenRouter Config
# ==============================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    ""
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-4o-mini"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


# ==============================
# Prompt
# ==============================

def build_grounded_prompt(query, context_text):

    return f"""

أنت مساعد ذكي لخدمات الأحوال المدنية المصرية.

استخدم فقط المعلومات الموجودة في المستندات.

القواعد:
- إذا وجدت الإجابة في المستندات أجب بشكل واضح.
- إذا لم توجد معلومات كافية قل:
"لا أملك معلومات كافية في المستندات المتاحة للإجابة على هذا السؤال."
- لا تخترع معلومات.
- لا تستخدم معلومات خارج المستندات.
- أجب بالعربية.


السؤال:
{query}


المستندات:
{context_text}

"""


# ==============================
# LLM Call
# ==============================

def call_openrouter(prompt):

    if not OPENROUTER_API_KEY:

        return (
            "لا يوجد مفتاح OpenRouter."
        )


    headers = {

        "Authorization":
        f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
        "application/json"

    }


    payload = {

        "model": OPENROUTER_MODEL,

        "messages":[
            {
                "role":"user",
                "content":prompt
            }
        ],

        "temperature":0

    }


    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=60
    )


    data = response.json()


    return (
        data["choices"][0]
        ["message"]
        ["content"]
        .strip()
    )



# ==============================
# Main Function
# ==============================

def answer_question(
        query,
        k=4,
        word_budget=200,
        max_chunks=3
):


    package = build_context_package(
        query,
        k=k,
        word_budget=word_budget,
        max_chunks=max_chunks
    )


    # مهم جداً
    # لو مفيش context لا نكلم الـ LLM

    if not package["context_text"]:

        return {

            "query":query,

            "answer":
            "لا أملك معلومات كافية في المستندات المتاحة للإجابة على هذا السؤال.",

            "sources":[]

        }


    prompt = build_grounded_prompt(
        query,
        package["context_text"]
    )


    answer = call_openrouter(prompt)


    return {

        "query":query,

        "answer":answer,

        "sources":
        package["sources"]

    }
