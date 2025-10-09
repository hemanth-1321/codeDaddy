import os
import requests

GITHUB_API_URL = "https://api.github.com"

def post_pr_comment(repo_name: str, pr_number: int, comment_body: str):
    """
    Post a markdown comment to a GitHub PR using the REST API.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not set in environment")

    url = f"{GITHUB_API_URL}/repos/{repo_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    data = {"body": comment_body}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print(f"✅ Comment successfully posted to PR #{pr_number} in {repo_name}")
    else:
        print(f"❌ Failed to post comment: {response.status_code} -> {response.text}")
        response.raise_for_status()
