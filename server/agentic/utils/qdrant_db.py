import os
import uuid
import json
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct, VectorParams, HnswConfig, Distance
from dotenv import load_dotenv
from typing import Dict, List
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

collection_name = "pr_context"

URL = os.getenv("QDRANT_DB")
API_KEY = os.getenv("QDRANT_API_KEY")

if not URL:
    raise ValueError("QDRANT_DB environment variable is missing")

if not API_KEY:
    raise ValueError("QDRANT_API_KEY environment variable is missing")
 
# Initialize Qdrant
qdrant_client = QdrantClient(url=URL, api_key=API_KEY)
print("Qdrant client initialized successfully")

# Initialize embeddings
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found")

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
VECTOR_DIM = len(embeddings.embed_query("dimension test"))
print(f"✓ Embedding dimension detected: {VECTOR_DIM}")

# Check or create collection with optimized HNSW indexing
collections = [c.name for c in qdrant_client.get_collections().collections]
if collection_name not in collections:
    print(f"Creating Qdrant collection '{collection_name}' with HNSW index...")
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=VECTOR_DIM,
            distance=Distance.COSINE,
            hnsw_config=HnswConfig(
                m=16,            # neighbors per node (memory vs accuracy tradeoff)
                ef_construct=200 # index build accuracy
            )
        ),
        shard_number=6,
        replication_factor=2,
    )
    print(f"Collection '{collection_name}' created successfully!")
else:
    print(f"Collection '{collection_name}' already exists")

def prepare_and_store_context(pr_contexts: List[Dict]):
    """
    Store multiple PR contexts in a single batch for efficiency.
    pr_contexts: List of dicts with keys - pr_number, repo_name, txt_data, json_data
    """
    points = []

    for ctx in pr_contexts:
        pr_number = ctx["pr_number"]
        repo_name = ctx["repo_name"]
        txt_data = ctx.get("txt_data")
        json_data = ctx.get("json_data")

        content = f"PR #{pr_number} - Repo: {repo_name}\n\n"
        if txt_data:
            content += f"--- TXT Context ---\n{txt_data}\n\n"
        if json_data:
            content += f"--- JSON Context ---\n{json.dumps(json_data, indent=2)}\n"

        vector = embeddings.embed_query(content)

        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "pr_number": pr_number,
                "repo_name": repo_name,
                "ref_id": f"{repo_name}_{pr_number}",
                "content": content,
            },
        ))

    # Upsert all points in one call (faster for large batches)
    qdrant_client.upsert(collection_name=collection_name, points=points)
    print(f"[Agent] Stored batch of {len(points)} PR contexts in Qdrant")
