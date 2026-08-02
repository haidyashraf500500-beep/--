# تعديل داخل 06_retrieve_context.py لتفادي استهلاك الـ RAM مبكراً

def _get_collection():
    """Return the persistent collection safely with lazy loading."""
    import os
    import importlib.util
    
    module_path = os.path.dirname(__file__)
    store_path = os.path.join(module_path, "05_create_chroma_store.py")
    vector_path = os.path.join(module_path, "04_vector_representation.py")
    
    # استدعاء ديناميكي خفيف للذاكرة
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
    import os
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
