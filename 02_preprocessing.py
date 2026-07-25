# -*- coding: utf-8 -*-
"""
02_preprocessing.py
====================
Stage 2 of the pipeline: preprocessing.

documents -> [preprocessing] -> chunking -> vector representation -> vector store
-> context retrieval -> prompting -> Streamlit UI

Loads DOCUMENTS from 01_documents.py (numbered filenames cannot be imported
with a plain `import 01_documents`, so we load the file directly by path) and
produces PROCESSED_DOCUMENTS: the same documents with Arabic-aware text
cleaning applied to the `text` field.
"""

import importlib.util
import os
import re


def _load_module(filename: str, alias: str):
    """Load a sibling .py file whose name starts with a digit (e.g. '01_documents.py')."""
    module_path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(alias, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_documents_module = _load_module("01_documents.py", "stage01_documents")
DOCUMENTS = _documents_module.DOCUMENTS

# Arabic diacritics (tashkeel) range - safe to strip for retrieval purposes.
TASHKEEL_PATTERN = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]")


def clean_arabic_text(text: str) -> str:
    """Normalize Arabic text extracted from a PDF or typed by hand.

    - removes diacritics (tashkeel)
    - splits digits glued to Arabic words (a common PDF-extraction artifact,
      e.g. "عاماً15" -> "عاماً 15")
    - collapses repeated whitespace / blank lines
    """
    text = TASHKEEL_PATTERN.sub("", text)
    text = re.sub(r"(?<=[\u0600-\u06FF])(?=[0-9])", " ", text)
    text = re.sub(r"(?<=[0-9])(?=[\u0600-\u06FF])", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def preprocess_documents(documents):
    processed = []
    for doc in documents:
        processed_doc = dict(doc)
        processed_doc["text"] = clean_arabic_text(doc["text"])
        processed_doc["word_count"] = len(processed_doc["text"].split())
        processed.append(processed_doc)
    return processed


PROCESSED_DOCUMENTS = preprocess_documents(DOCUMENTS)


def main() -> None:
    print(f"Preprocessed {len(PROCESSED_DOCUMENTS)} documents\n")
    for doc in PROCESSED_DOCUMENTS:
        print(f"  [{doc['document_id']}] {doc['title']} - {doc['word_count']} words")


if __name__ == "__main__":
    main()
