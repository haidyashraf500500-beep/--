# -*- coding: utf-8 -*-
"""
03_chunking.py
==============
Stage 3 of the pipeline: chunking.

documents -> preprocessing -> [chunking] -> vector representation -> vector store
-> context retrieval -> prompting -> Streamlit UI

Loads PROCESSED_DOCUMENTS from 02_preprocessing.py and splits every document
into fixed-size, overlapping word-window chunks. The overlap keeps a rule and
its exception (or a fee and its duration) from being torn apart between two
chunks.
"""

import importlib.util
import os


def _load_module(filename: str, alias: str):
    module_path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(alias, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_preprocessing_module = _load_module("02_preprocessing.py", "stage02_preprocessing")
PROCESSED_DOCUMENTS = _preprocessing_module.PROCESSED_DOCUMENTS

CHUNK_SIZE = 45
CHUNK_OVERLAP = 12


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    words = text.split()

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap
    return chunks


def build_chunks(documents):
    chunks = []
    for doc in documents:
        for chunk_index, chunk_body in enumerate(chunk_text(doc["text"])):
            chunks.append(
                {
                    "chunk_id": f"d{doc['document_id']}_c{chunk_index}",
                    "document_id": doc["document_id"],
                    "sector": doc["sector"],
                    "doc_type": doc["doc_type"],
                    "title": doc["title"],
                    "chunk_index": chunk_index,
                    "chunk_text": chunk_body,
                    "word_count": len(chunk_body.split()),
                    # search_text = what actually gets embedded / indexed.
                    # Prepending title + sector boosts lexical and semantic
                    # matches for queries that mention the service by name.
                    "search_text": f"{doc['title']} {doc['sector']} {chunk_body}",
                }
            )
    return chunks


CHUNKS = build_chunks(PROCESSED_DOCUMENTS)


def main() -> None:
    print(f"Built {len(CHUNKS)} chunks from {len(PROCESSED_DOCUMENTS)} documents\n")
    by_doc = {}
    for chunk in CHUNKS:
        by_doc.setdefault(chunk["document_id"], []).append(chunk)
    for document_id, doc_chunks in sorted(by_doc.items()):
        title = doc_chunks[0]["title"]
        avg_words = sum(c["word_count"] for c in doc_chunks) / len(doc_chunks)
        print(f"  doc {document_id} ({title}): {len(doc_chunks)} chunks, avg {avg_words:.1f} words")


if __name__ == "__main__":
    main()
