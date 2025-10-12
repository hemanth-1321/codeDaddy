import os
import hmac
import hashlib
import json
from server.worker.main import process_pr
from dotenv import load_dotenv
from fastapi import APIRouter, Request, HTTPException
from redis import Redis
from rq import Queue, Retry 
from server.servcies.github import post_pr_comment

load_dotenv()

router = APIRouter()

REDIS_URL = os.getenv("REDIS_URL")
print("redis url", REDIS_URL)
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


def post_progress_comment(pr_number: int, owner: str, repo: str, installation_id: int) -> int:
    """
    loader comment
    """
    
    progress_body = """## 📝 Note

        Currently processing new changes in this PR. This may take a few minutes, please wait...

        <details>
        <summary>📦 Commits</summary>

        > Analyzing commits...

        </details>

        <details>
        <summary>📁 Files selected for processing</summary>

        > Scanning files...

        </details>

        ---

        *Powered by CodeDaddy 🧔🏻‍♂️*
        """
            
    try:
        response = post_pr_comment(pr_number, owner, repo, progress_body, installation_id)
        comment_id = response.get("id")
        print(f"[Progress] Posted progress comment ID: {comment_id}")
        return comment_id
    except Exception as e:
        print(f"[Progress] Failed to post progress comment: {e}")
        return None
    

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
            installation_id = int(os.getenv("GITHUB_INSTALLATION_ID", "0"))
            
            pr_number = payload.get("number")
            repo_name = repo.get("full_name")
            owner, repo_name_only = repo_name.split("/")
            
            comment_id = post_progress_comment(pr_number, owner, repo_name_only, installation_id)
            
            pr_data = {
                "pr_number": pr_number,
                "base_branch": pr.get("base", {}).get("ref"),
                "head_branch": pr.get("head", {}).get("ref"),
                "clone_url": repo.get("clone_url"),
                "repo_name": repo_name,
                "action": action,
                "commit_sha": pr.get("head", {}).get("sha"),
                "progress_comment_id": comment_id, 
                "installation_id": installation_id,
                "owner": owner,
                "repo": repo_name_only
            }

            print("Enqueuing PR:", pr_data)
            queue.enqueue(process_pr, pr_data, retry=Retry(max=3, interval=[10, 30, 60])) 

            return {"status": "queued", "pr": pr_data, "progress_comment_id": comment_id}

    return {"status": "ignored"}