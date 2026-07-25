# -*- coding: utf-8 -*-
"""
04_vector_representation.py
============================
Stage 4 of the pipeline: vector representation.

documents -> preprocessing -> chunking -> [vector representation] -> vector store
-> context retrieval -> prompting -> Streamlit UI

Loads CHUNKS from 03_chunking.py and turns each chunk's `search_text` into a
dense embedding vector using a multilingual sentence-transformers model
(needed because the corpus is Arabic).
"""

import importlib.util
import os

import numpy as np
from sentence_transformers import SentenceTransformer


def _load_module(filename: str, alias: str):
    module_path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(alias, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_chunking_module = _load_module("03_chunking.py", "stage03_chunking")
CHUNKS = _chunking_module.CHUNKS

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

_model = None


def get_embedding_model() -> SentenceTransformer:
    """Lazily load (and cache) the embedding model so importing this file is cheap."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def embed_texts(texts):
    model = get_embedding_model()
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)


def build_chunk_embeddings(chunks):
    texts = [chunk["search_text"] for chunk in chunks]
    return embed_texts(texts)


def main() -> None:
    embeddings = build_chunk_embeddings(CHUNKS)
    print(f"Embedded {len(CHUNKS)} chunks with '{EMBEDDING_MODEL_NAME}'")
    print(f"Embedding matrix shape: {embeddings.shape}")
    print(f"Example vector norm (should be ~1.0): {np.linalg.norm(embeddings[0]):.4f}")


if __name__ == "__main__":
    main()
