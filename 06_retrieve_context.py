# -*- coding: utf-8 -*-
"""
06_retrieve_context.py
=======================
Stage 6 of the pipeline: context retrieval (Memory Optimized for Streamlit Cloud).
"""

import os

def _get_collection():
    """Return the persistent collection safely with lazy loading to save RAM."""
    import importlib.util
    
    module_path = os.path.dirname(__file__)
    store_path = os.path.join(module_path, "05_create_chroma_store.py")
    
    spec_store = importlib.util.spec_from_file_location("stage05", store_path)
    _store_module = importlib.util.module_from_spec(spec_store)
    spec_store.loader.exec_module(_store_module)
    
    CHROMA_DIR = _store_module.CHROMA_DIR
    COLLECTION_NAME = _store_module.COLLECTION_NAME
    get_chroma_client = _store_module.get_chroma_client
    
    client = get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def retrieve_chunks(query: str, k: int = 6):
    """Query the vector store and return a list of chunk dicts with a score."""
    import importlib.util
    
    module_path = os.path.dirname(__file__)
    vector_path = os.path.join(module_path, "04_vector_representation.py")
    
    spec_vec = importlib.util.spec_from_file_location("stage04", vector_path)
    _vector_module = importlib.util.module_from_spec(spec_vec)
    spec_vec.loader.exec_module(_vector_module)
    
    embed_texts = _vector_module.embed_texts

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
    """Turn raw retrieved chunks into a clean, word-budgeted context block."""
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
