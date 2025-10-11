import os
import json
from redis import Redis
from server.agentic.utils.qdrant_db import prepare_and_store_context
from server.agentic.agents.graph import workflow
from server.agentic.agents.nodes import PRState

redis_conn = Redis(host="localhost", port=6379, db=0)
queue_name = "pr_context_queue"

def process_ai_job(job_data: dict):
    pr_number = job_data.get("pr_number")
    repo_name = job_data.get("repo_name")
    commit_sha = job_data.get("commit_sha")
    context_json_path = job_data.get("context_json")
    context_txt_path = job_data.get("context_txt")

    json_data = {}
    txt_data = ""

    if context_json_path and os.path.exists(context_json_path):
        with open(context_json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

    if context_txt_path and os.path.exists(context_txt_path):
        with open(context_txt_path, "r", encoding="utf-8") as f:
            txt_data = f.read()

    prepare_and_store_context(pr_number, repo_name, txt_data, json_data)

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
        review_complete=False
    )

    workflow.invoke(state)

    # Clean up context files
    for path in [context_json_path, context_txt_path]:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
