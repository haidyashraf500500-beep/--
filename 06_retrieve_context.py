# -*- coding: utf-8 -*-

"""
06_retrieve_context.py
Stage 6: Context Retrieval
"""

import importlib.util
import os


def _load_module(filename: str, alias: str):
    module_path = os.path.join(os.path.dirname(__file__), filename)

    spec = importlib.util.spec_from_file_location(
        alias,
        module_path
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


# Load previous stages
_store_module = _load_module(
    "05_create_chroma_store.py",
    "stage05_create_chroma_store"
)

_vector_module = _load_module(
    "04_vector_representation.py",
    "stage04_vector_representation"
)


CHROMA_DIR = _store_module.CHROMA_DIR
COLLECTION_NAME = _store_module.COLLECTION_NAME

get_chroma_client = _store_module.get_chroma_client
create_chroma_store = _store_module.create_chroma_store

embed_texts = _vector_module.embed_texts



def _get_collection():

    if not os.path.isdir(CHROMA_DIR):
        create_chroma_store()

    client = get_chroma_client()

    return client.get_or_create_collection(
        name=COLLECTION_NAME
    )



def retrieve_chunks(query: str, k: int = 6):

    collection = _get_collection()

    query_embedding = embed_texts([query])[0].tolist()


    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )


    retrieved = []


    for chunk_id, chunk_text, metadata, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):

        similarity_score = 1 - distance


        retrieved.append(
            {
                "chunk_id": chunk_id,
                "chunk_text": chunk_text,
                "score": similarity_score,
                **metadata
            }
        )


    return retrieved




def build_context_package(
        query: str,
        k: int = 6,
        word_budget: int = 250,
        max_chunks: int = 4
):


    candidates = sorted(
        retrieve_chunks(query, k=k),
        key=lambda x: x["score"],
        reverse=True
    )


    # مهم جدا:
    # لو النتائج مش قريبة من السؤال نعتبرها غير موجودة
    SIMILARITY_THRESHOLD = 0.55


    candidates = [
        c for c in candidates
        if c["score"] >= SIMILARITY_THRESHOLD
    ]



    selected = []
    seen_ids = set()
    used_words = 0



    for chunk in candidates:


        if chunk["chunk_id"] in seen_ids:
            continue


        if len(selected) >= max_chunks:
            break



        words = len(
            chunk["chunk_text"].split()
        )


        if used_words + words > word_budget:
            continue



        selected.append(chunk)

        seen_ids.add(
            chunk["chunk_id"]
        )

        used_words += words




    # مفيش context مناسب
    if not selected:

        return {
            "query": query,
            "candidates": [],
            "selected_chunks": [],
            "sources": [],
            "context_text": "",
            "used_words": 0
        }




    context_text = "\n\n".join(
        [
            f"[المصدر: {c.get('title','Unknown')}]\n{c['chunk_text']}"
            for c in selected
        ]
    )



    return {

        "query": query,

        "candidates": candidates,

        "selected_chunks": selected,

        "sources": sorted(
            {
                c.get(
                    "title",
                    "Unknown"
                )
                for c in selected
            }
        ),

        "context_text": context_text,

        "used_words": used_words
    }



def main():

    q = "كيف أعمل بطاقة لأول مرة؟"

    result = build_context_package(q)


    print(result["context_text"])



if __name__ == "__main__":
    main()
