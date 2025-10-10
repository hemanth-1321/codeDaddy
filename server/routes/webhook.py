import hmac
import hashlib

from fastapi import APIRouter,Request,HTTPException
from redis import Redis
from rq import Queue
from worker.main import process_pr
router=APIRouter()

connection=Redis(host="localhost",port=6379,db=0)
queue=Queue("github_prs",connection=connection)

WEBHOOK_SECRET="hemanth"

def verify_signature(payload: bytes, signature: str) -> bool:
    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/github")
async def webhook(request:Request):
    signature=request.headers.get("X-Hub-Signature-256")
    if not signature:   
        raise HTTPException(status_code=403,detail="missing signature")
    body=await request.body()
    if not verify_signature(body,signature):
        raise HTTPException(status_code=404,detail="invalid signature")
    
    event=request.headers.get("X-GitHub-Event")
    payload=await request.json()
    if event=="pull_request" and payload:
        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {})
        action=payload.get("action")
        if action in ["opened", "reopened", "synchronize"]:
             pr_data = {
            "pr_number": payload.get("number"),
            "base_branch": pr.get("base", {}).get("ref"),
            "head_branch": pr.get("head", {}).get("ref"),
            "clone_url": repo.get("clone_url"),
            "repo_name": repo.get("full_name"),
            "action": payload.get("action"),
            "commit_sha": pr.get("head", {}).get("sha"),
        }

       
        
        print("pr",pr)
        queue.enqueue(process_pr, pr_data)
        return {"status": "queued", "pr": pr_data}
    
    
    
    
    
    #rq worker github_prs 