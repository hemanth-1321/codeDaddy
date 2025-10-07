import os
import json
from redis import Redis
from agentic.utils.qdrant_db import prepare_and_store_context


redis_conn = Redis(host="localhost", port=6379, db=0)
queue_name = "pr_context_queue"

def process_ai_job(job_data: dict):
    """
    Reads the TXT and JSON context files from the queue job and prints them.
    """
    pr_number = job_data.get("pr_number")
    repo_name = job_data.get("repo_name")

    context_json_path = job_data.get("context_json")
    context_txt_path = job_data.get("context_txt")

    print(f"\n[Agent] ✅ Processing PR #{pr_number} from {repo_name}")

    # Read JSON context
    if context_json_path and os.path.exists(context_json_path):
        with open(context_json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        print(f"\n--- JSON Context ({context_json_path}) ---")
        print(json.dumps(json_data, indent=2))
    else:
        print(f"[Agent] ❌ JSON context not found: {context_json_path}")

    # Read TXT context
    if context_txt_path and os.path.exists(context_txt_path):
        with open(context_txt_path, "r", encoding="utf-8") as f:
            txt_data = f.read()
        print(f"\n--- TXT Context ({context_txt_path}) ---")
        print(txt_data)
    else:
        print(f"[Agent] ❌ TXT context not found: {context_txt_path}")
        
    prepare_and_store_context(pr_number,repo_name,txt_data,json_data)

    print(f"[Agent] ✅ Done processing PR #{pr_number}\n")
