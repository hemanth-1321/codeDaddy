import os
import json
import tempfile
import boto3
from redis import Redis
from server.agentic.utils.qdrant_db import prepare_and_store_context
from server.agentic.agents.graph import workflow
from server.agentic.agents.nodes import PRState
from rq import Queue

REDIS_URL = os.getenv("REDIS_URL")
try:
    connection = Redis.from_url(REDIS_URL, decode_responses=False)
    connection.ping()
    print("[Worker] Connected to Redis successfully")
except Exception as e:
    print("[Worker] Redis connection failed:", e)
    raise

queue = Queue("pr_context_queue", connection=connection)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

def download_s3_file(s3_uri):
    """Download S3 file to a temp location and return local path."""
    if not s3_uri.startswith("s3://"):
        raise ValueError("Invalid S3 URI")

    _, bucket_key = s3_uri.split("s3://", 1)
    bucket, key = bucket_key.split("/", 1)
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    s3_client.download_file(bucket, key, tmp_file.name)
    return tmp_file.name

def delete_s3_file(s3_uri):
    """Delete a file from S3."""
    if not s3_uri or not s3_uri.startswith("s3://"):
        return
    
    try:
        _, bucket_key = s3_uri.split("s3://", 1)
        bucket, key = bucket_key.split("/", 1)
        s3_client.delete_object(Bucket=bucket, Key=key)
        print(f"[S3] Deleted: {s3_uri}")
    except Exception as e:
        print(f"[S3] Failed to delete {s3_uri}: {e}")

def process_ai_job(job_data: dict):
    print("Received job",  job_data)
    pr_number = job_data.get("pr_number")
    repo_name = job_data.get("repo_name")
    commit_sha = job_data.get("commit_sha")
    context_json_uri = job_data.get("context_json")
    context_txt_uri = job_data.get("context_txt")
    
    # NEW: Extract progress comment info
    progress_comment_id = job_data.get("progress_comment_id")
    installation_id = job_data.get("installation_id")
    owner = job_data.get("owner")
    repo = job_data.get("repo")

    json_data = {}
    txt_data = ""
    local_json_path = local_txt_path = None

    try:
        if context_json_uri:
            local_json_path = download_s3_file(context_json_uri)
            with open(local_json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

        if context_txt_uri:
            local_txt_path = download_s3_file(context_txt_uri)
            with open(local_txt_path, "r", encoding="utf-8") as f:
                txt_data = f.read()

        prepare_and_store_context([{
            "pr_number": pr_number,
            "repo_name": repo_name,
            "txt_data": txt_data,
            "json_data": json_data
        }])


        state = PRState(
            pr_number=int(pr_number) if pr_number else 0,
            repo_name=str(repo_name) if repo_name else "",
            diff_content=txt_data,
            pr_description=json_data.get("description", "") if json_data else "",
            similar_prs=[],
            security_issues=[],
            code_quality_issues=[],
            performance_issues=[],
            test_suggestions=[],
            learnings="",
            final_review="",
            commit_sha=commit_sha,
            review_complete=False,
            progress_comment_id=progress_comment_id,
            installation_id=installation_id,
            owner=owner,
            repo=repo
        )

        print(f"Starting workflow with progress_comment_id: {progress_comment_id}")
        workflow.invoke(state)
        print("Workflow completed successfully")

    except Exception as e:
        print(f"Error in process_ai_job: {e}")
        raise
    finally:
        delete_s3_file(context_json_uri)
        delete_s3_file(context_txt_uri)