# -*- coding: utf-8 -*-
"""
07_prompting.py
================
Stage 7 of the pipeline: prompting.
"""

import importlib.util
import os
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def _load_module(filename: str, alias: str):
    module_path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(alias, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

_retrieval_module = _load_module("06_retrieve_context.py", "stage06_retrieve_context")
build_context_package = _retrieval_module.build_context_package

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def build_grounded_prompt(query: str, context_text: str) -> str:
    return f"""أنت مساعد حكومي لخدمات الأحوال المدنية المصرية. أجب على السؤال الموجه لك بناءً على السياق المرفق أدناه فقط.
إذا لم تجد الإجابة في السياق، قل بوضوح: "عذراً، لا أمتلك معلومات كافية للإجابة على هذا السؤال بناءً على المستندات الرسمية المتاحة."

السؤال:
{query}

السياق:
{context_text}
"""

def call_openrouter(prompt: str, model: str = None, temperature: float = 0.0) -> str:
    model = model or OPENROUTER_MODEL

    if not OPENROUTER_API_KEY:
        return "لا يوجد مفتاح OPENROUTER_API_KEY متاح."

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

def answer_question(query: str, k: int = 6, word_budget: int = 220, max_chunks: int = 4, similarity_threshold: float = 0.0) -> dict:
    """إرسال السؤال واسترجاع الإجابة بمرونة تامة بدون شروط معقدة"""
    package = build_context_package(query, k=k, word_budget=word_budget, max_chunks=max_chunks)

    prompt = build_grounded_prompt(package["query"], package["context_text"])
    answer_text = call_openrouter(prompt)

    sources = package["sources"]
    if "لا أمتلك معلومات كافية" in answer_text or "عذراً" in answer_text:
        sources = []

    return {
        "query": query,
        "answer": answer_text,
        "sources": sources,
        "context_text": package["context_text"],
        "prompt": prompt,
    }
