from typing import  List,Dict
from .qdrant_db import embeddings,qdrant_client,collection_name




def search_vector_tool(query:str,limit:int=10)->List[Dict]:
    """
    simple vector search wrapper used by agents
    """
    query_vector=embeddings.embed_query(query)
    
    results=qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit
    )
    out=[]
    for r in results:
        payload=r.payload or {}
        out.append({
            "ref_id": payload.get("ref_id"),
            "content": payload.get("content", "")[:1000],
            "score": round(getattr(r, "score", 0) or 0, 4)
        })
    return out
   
   
# res=search_vector_tool(query="PR #103 - Repo: hemanth-1321/testBase branch: main, Head branch: m")

# print("res",res)


def search_learnings_tool(query: str, limit: int = 5) -> List[Dict]:
    """
    Search the Qdrant 'pr_learnings' collection for similar AI learnings + human corrections.
    """
    query_vector = embeddings.embed_query(query)
    results = qdrant_client.search(
        collection_name="pr_learnings",
        query_vector=query_vector,
        limit=limit
    )
    out = []
    for r in results:
        payload = r.payload or {}
        out.append({
            "ref_id": payload.get("pr_number", ""),
            "content": payload.get("content", "")[:1000],
            "learnings": payload.get("learnings", {}),
            "human_feedback": payload.get("human_feedback", ""),
            "score": round(getattr(r, "score", 0) or 0, 4)
        })
    return out
