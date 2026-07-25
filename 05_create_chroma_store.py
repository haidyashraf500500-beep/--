# -*- coding: utf-8 -*-
"""
05_create_chroma_store.py
==========================
Stage 5 of the pipeline: vector store.

documents -> preprocessing -> chunking -> vector representation -> [vector store]
-> context retrieval -> prompting -> Streamlit UI

Loads CHUNKS from 03_chunking.py and the embedding helpers from
04_vector_representation.py, then writes everything into a persistent Chroma
collection on disk. Run this file once (or whenever the source documents
change) to (re)build the store that 06_retrieve_context.py reads from.
"""

import importlib.util
import os
import shutil

import chromadb


def _load_module(filename: str, alias: str):
    module_path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(alias, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_chunking_module = _load_module("03_chunking.py", "stage03_chunking")
_vector_module = _load_module("04_vector_representation.py", "stage04_vector_representation")

CHUNKS = _chunking_module.CHUNKS
build_chunk_embeddings = _vector_module.build_chunk_embeddings
EMBEDDING_MODEL_NAME = _vector_module.EMBEDDING_MODEL_NAME

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_store")
COLLECTION_NAME = "civil_status_chunks"


def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=CHROMA_DIR)


def create_chroma_store(chunks=CHUNKS, rebuild: bool = True) -> chromadb.api.models.Collection.Collection:
    """Create (or rebuild) the persistent Chroma collection from CHUNKS."""
    if rebuild and os.path.isdir(CHROMA_DIR):
        shutil.rmtree(CHROMA_DIR)

    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"embedding_model": EMBEDDING_MODEL_NAME},
    )

    embeddings = build_chunk_embeddings(chunks)

    collection.add(
        ids=[chunk["chunk_id"] for chunk in chunks],
        embeddings=embeddings.tolist(),
        documents=[chunk["chunk_text"] for chunk in chunks],
        metadatas=[
            {
                "document_id": chunk["document_id"],
                "sector": chunk["sector"],
                "doc_type": chunk["doc_type"],
                "title": chunk["title"],
                "chunk_index": chunk["chunk_index"],
            }
            for chunk in chunks
        ],
    )
    return collection


def main() -> None:
    collection = create_chroma_store()
    print(f"Chroma store built at: {CHROMA_DIR}")
    print(f"Collection '{COLLECTION_NAME}' now has {collection.count()} vectors")


if __name__ == "__main__":
    main()
