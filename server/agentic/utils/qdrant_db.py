import os
import uuid
import json
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct
from dotenv import load_dotenv
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

# Check or create collection
collections = [c.name for c in qdrant_client.get_collections().collections]
if collection_name not in collections:
    print(f"Creating Qdrant collection '{collection_name}'...")
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        shard_number=6,
        replication_factor=2,
    )
else:
    print(f"Collection '{collection_name}' already exists")

# Initialize embeddings
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found")

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# Store PR context in Qdrant
def prepare_and_store_context(pr_number, repo_name, txt_data, json_data):
    content = f"PR #{pr_number} - Repo: {repo_name}\n\n"
    if txt_data:
        content += f"--- TXT Context ---\n{txt_data}\n\n"
    if json_data:
        content += f"--- JSON Context ---\n{json.dumps(json_data, indent=2)}\n"

    vector = embeddings.embed_query(content)

    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={
            "pr_number": pr_number,
            "repo_name": repo_name,
            "ref_id":f"{repo_name}_{pr_number}",
            "content": content,
        },
    )

    qdrant_client.upsert(collection_name=collection_name, points=[point])
    
    print(f"[Agent] Context stored in Qdrant for PR #{pr_number}")

