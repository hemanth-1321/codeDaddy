from typing import List, Dict
from .qdrant_db import embeddings, qdrant_client, collection_name, VECTOR_DIM

def search_vector_tool(query: str, limit: int = 10) -> list[dict]:
    """
    Simple vector search wrapper used by agents
    """
    query_vector = embeddings.embed_query(query)

    results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit
    )
    print("")
    out = []
    for r in results:
        payload = r.payload or {}
        out.append({
            "ref_id": payload.get("ref_id"),
            "content": payload.get("content", ""),
            "score": round(getattr(r, "score", 0) or 0, 4)
        })


    return out

