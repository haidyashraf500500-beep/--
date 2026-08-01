# -*- coding: utf-8 -*-

"""
07_prompting.py
Stage 7: Prompting
"""

import importlib.util
import os
import requests


# ===============================
# Load dotenv
# ===============================

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass



# ===============================
# Load module helper
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



# ===============================
# Load Retrieval Stage
# ===============================

_retrieval_module = _load_module(
    "06_retrieve_context.py",
    "stage06_retrieve_context"
)


build_context_package = (
    _retrieval_module.build_context_package
)



# ===============================
# OpenRouter Config
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
# Build Prompt
# ===============================

def build_grounded_prompt(
        query: str,
        context_text: str
):

    return f"""

أنت مساعد ذكي لخدمات الأحوال المدنية المصرية.

مهمتك الإجابة على سؤال المستخدم باستخدام المستندات فقط.

القواعد:

1- استخدم المعلومات الموجودة في المستندات فقط.

2- لا تستخدم معلومات خارجية.

3- لا تخترع أي خطوات أو رسوم أو شروط.

4- إذا كانت الإجابة موجودة في المستندات:
قدمها بشكل مرتب وواضح.

5- إذا لم تكن الإجابة موجودة:
اكتب فقط:
"لا أملك معلومات كافية في المستندات المتاحة للإجابة على هذا السؤال."

6- لا تذكر أي مصدر غير موجود في المستندات.

7- أجب باللغة العربية البسيطة.


السؤال:
{query}


المستندات:
{context_text}

"""




# ===============================
# Call LLM
# ===============================

def call_openrouter(
        prompt: str,
        model: str = None,
        temperature: float = 0.0
):

    model = model or OPENROUTER_MODEL


    if not OPENROUTER_API_KEY:

        return (
            "لا يوجد مفتاح OPENROUTER_API_KEY."
        )



    headers = {

        "Authorization":
        f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
        "application/json"

    }



    payload = {

        "model": model,

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],

        "temperature": temperature

    }



    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()


    except Exception as e:

        return f"OpenRouter error: {e}"



    data = response.json()



    try:

        return (
            data["choices"][0]
            ["message"]
            ["content"]
            .strip()
        )


    except Exception:

        return (
            "حدث خطأ في قراءة رد النموذج."
        )





# ===============================
# Main RAG Function
# ===============================

def answer_question(
        query: str,
        k: int = 6,
        word_budget: int = 250,
        max_chunks: int = 4
):


    package = build_context_package(

        query=query,

        k=k,

        word_budget=word_budget,

        max_chunks=max_chunks

    )



    # ===============================
    # No Context Found
    # ===============================

    if not package["context_text"].strip():


        return {

            "query": query,

            "answer":
            "لا أملك معلومات كافية في المستندات المتاحة للإجابة على هذا السؤال.",

            "sources": [],

            "context_text": "",

            "prompt": ""

        }




    # ===============================
    # Generate Answer
    # ===============================

    prompt = build_grounded_prompt(

        query,

        package["context_text"]

    )



    answer = call_openrouter(prompt)



    return {


        "query": query,


        "answer": answer,


        "sources":
        package["sources"],


        "context_text":
        package["context_text"],


        "prompt": prompt

    }
