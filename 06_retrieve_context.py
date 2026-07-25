# -*- coding: utf-8 -*-
"""
06_retrieve_context.py
=======================
Stage 6 of the pipeline: context retrieval.

documents -> preprocessing -> chunking -> vector representation -> vector store
-> [context retrieval] -> prompting -> Streamlit UI

Loads the Chroma collection helpers from 05_create_chroma_store.py and the
embedding helper from 04_vector_representation.py, then exposes
`build_context_package(query)`: retrieve top-k chunks for a query and pack
them into a word-budgeted, de-duplicated context block ready for a prompt.

If the store does not exist yet on disk, it is built automatically on first
import so this file (and everything downstream of it) works out of the box.
"""

import importlib.util
import os


def _load_module(filename: str, alias: str):
    module_path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(alias, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_store_module = _load_module("05_create_chroma_store.py", "stage05_create_chroma_store")
_vector_module = _load_module("04_vector_representation.py", "stage04_vector_representation")

CHROMA_DIR = _store_module.CHROMA_DIR
COLLECTION_NAME = _store_module.COLLECTION_NAME
get_chroma_client = _store_module.get_chroma_client
create_chroma_store = _store_module.create_chroma_store
embed_texts = _vector_module.embed_texts


def _get_collection():
    """Return the persistent collection, building it on first run if missing."""
    if not os.path.isdir(CHROMA_DIR):
        create_chroma_store()
    client = get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def retrieve_chunks(query: str, k: int = 6):
    """Query the vector store and return a list of chunk dicts with a score."""
    collection = _get_collection()
    query_embedding = embed_texts([query])[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
    )

    retrieved = []
    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for chunk_id, chunk_text, metadata, distance in zip(ids, documents, metadatas, distances):
        # Chroma returns cosine *distance*; convert to a similarity score in [0, 1].
        similarity_score = 1 - distance
        retrieved.append(
            {
                "chunk_id": chunk_id,
                "chunk_text": chunk_text,
                "score": similarity_score,
                **metadata,
            }
        )
    return retrieved


def build_context_package(query: str, k: int = 6, word_budget: int = 220, max_chunks: int = 4):
    """Turn raw retrieved chunks into a clean, word-budgeted context block.

    - orders candidates by similarity score
    - de-duplicates by chunk_id
    - stops once either max_chunks or word_budget is reached
    - keeps title metadata so the final answer can cite its sources
    """
    candidates = sorted(retrieve_chunks(query, k=k), key=lambda c: c["score"], reverse=True)

    selected = []
    seen_ids = set()
    used_words = 0

    for chunk in candidates:
        if chunk["chunk_id"] in seen_ids:
            continue
        if len(selected) >= max_chunks:
            break
        chunk_words = len(chunk["chunk_text"].split())
        if used_words + chunk_words > word_budget and selected:
            continue
        selected.append(chunk)
        seen_ids.add(chunk["chunk_id"])
        used_words += chunk_words

    context_blocks = [f"[المصدر: {c['title']}]\n{c['chunk_text']}" for c in selected]
    context_text = "\n\n".join(context_blocks)

    return {
        "query": query,
        "candidates": candidates,
        "selected_chunks": selected,
        "sources": sorted({c["title"] for c in selected}),
        "context_text": context_text,
        "used_words": used_words,
    }


def main() -> None:
    demo_query = "عايز رخصة قيادة خاصة، السن المطلوب كام والكشف الطبي بيشمل ايه؟"
    package = build_context_package(demo_query)
    print(f"Query: {demo_query}\n")
    print(f"Selected {len(package['selected_chunks'])} chunks, {package['used_words']} words\n")
    print("Sources:")
    for source in package["sources"]:
        print(f"  - {source}")
    print("\n--- Context text ---\n")
    print(package["context_text"])


if __name__ == "__main__":
    main()
