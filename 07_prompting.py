# -*- coding: utf-8 -*-

"""
07_prompting.py
Stage 7: Prompting + LLM Generation
"""

import importlib.util
import os
import requests


# ===============================
# Load Stage 6
# ===============================

def _load_module(filename: str, alias: str):

    module_path = os.path.join(
        os.path.dirname(__file__),
        filename
    )

    spec = importlib.util.spec_from_file_location(
        alias,
        module_path
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


retrieval = _load_module(
    "06_retrieve_context.py",
    "stage06"
)


build_context_package = retrieval.build_context_package



# ===============================
# OpenRouter Settings
# ===============================

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



# ===============================
# Prompt
# ===============================

def build_grounded_prompt(query, context):


    return f"""

أنت مساعد ذكي لخدمات الأحوال المدنية المصرية.

اعتمد فقط على المعلومات الموجودة في المستندات.

السؤال:
{query}


المستندات:
{context}


التعليمات:

1- إذا كانت الإجابة موجودة في المستندات:
قدم إجابة واضحة ومنظمة.

2- إذا لم توجد الإجابة نهائياً:
اكتب:
"لا أملك معلومات كافية في المستندات المتاحة للإجابة على هذا السؤال."

3- لا تخترع أي بيانات.

4- لا تستخدم معلومات خارج المستندات.

5- أجب باللغة العربية.


"""



# ===============================
# Call LLM
# ===============================

def call_openrouter(prompt):


    if not OPENROUTER_API_KEY:

        return "Missing API Key"


    headers = {

        "Authorization":
        f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
        "application/json"

    }


    data = {

        "model": OPENROUTER_MODEL,

        "messages":[
            {
                "role":"user",
                "content":prompt
            }
        ],

        "temperature":0

    }



    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=data,
            timeout=40
        )


        response.raise_for_status()


        result = response.json()


        return (
            result["choices"][0]
            ["message"]
            ["content"]
            .strip()
        )


    except Exception as e:

        return f"Error: {e}"



# ===============================
# Main RAG Function
# ===============================

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



    context = package["context_text"]



    # لو مفيش نتائج من Chroma

    if not context.strip():

        return {

            "query":query,

            "answer":
            "لا أملك معلومات كافية في المستندات المتاحة للإجابة على هذا السؤال.",

            "sources":[],

            "context_text":""

        }



    prompt = build_grounded_prompt(

        query,

        context

    )



    answer = call_openrouter(prompt)



    return {


        "query":query,


        "answer":answer,


        "sources":
        package["sources"],


        "context_text":
        context


    }
