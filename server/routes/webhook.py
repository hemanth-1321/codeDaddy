import os
import hmac
import hashlib
import json
import logging
from dotenv import load_dotenv
from fastapi import APIRouter, Request, HTTPException
from redis import Redis
from rq import Queue

load_dotenv()

router = APIRouter()

REDIS_URL = os.getenv("REDIS_URL")
print("redis url",REDIS_URL)
if not REDIS_URL:
    raise RuntimeError("REDIS_URL is not set")

try:
    connection = Redis.from_url(REDIS_URL, decode_responses=False)
    connection.ping()
    print("Connected to Redis successfully")
except Exception as e:
    print("Redis connection failed:", e)
    raise

queue = Queue("github_prs", connection=connection)

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "hemanth")


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature"""
    if not signature:
        return False

    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_sig = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected_sig, signature)


@router.post("/github")
async def webhook(request: Request):
    signature = request.headers.get("X-Hub-Signature-256", "")

    body = await request.body()
    if not verify_signature(body, signature):
        raise HTTPException(status_code=403, detail="invalid signature")

    try:
        payload = json.loads(body)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")

    event = request.headers.get("X-GitHub-Event", "")
    if event == "pull_request" and payload:
        action = payload.get("action")
        if action in ["opened", "reopened", "synchronize"]:
            pr = payload.get("pull_request", {})
            repo = payload.get("repository", {})
            pr_data = {
                "pr_number": payload.get("number"),
                "base_branch": pr.get("base", {}).get("ref"),
                "head_branch": pr.get("head", {}).get("ref"),
                "clone_url": repo.get("clone_url"),
                "repo_name": repo.get("full_name"),
                "action": action,
                "commit_sha": pr.get("head", {}).get("sha"),
            }

            print("Enqueuing PR:", pr_data)
            queue.enqueue("server.worker.main.process_pr_docker", pr_data)

            return {"status": "queued", "pr": pr_data}

    return {"status": "ignored"}
