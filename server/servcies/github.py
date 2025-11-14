import requests
from fastapi import HTTPException,Query
from server.utils.generate_app_jwt import get_installations_headers

# change everything to async ,replacing requests with  httpx => httpx.AsyncClient()


def get_installation_access_token(installation_id: int) -> str:
    """
    Create an installation access token for a specific GitHub App installation.
    Requires the App JWT from get_installations_headers().
    """
    token_url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = get_installations_headers()  # contains: Authorization: Bearer <APP_JWT>
    res = requests.post(token_url, headers=headers)

    if res.status_code != 201:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    return res.json()["token"]




def get_user_installations(username: str):
    """
    Fetch installation details by GitHub username (login).
    """
    headers = get_installations_headers()

    # Get all installations for the app
    res = requests.get("https://api.github.com/app/installations", headers=headers)
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    installations = res.json()

    # Find installation(s) that belong to the given username
    matching_installations = [
        inst for inst in installations
        if inst.get("account", {}).get("login", "").lower() == username.lower()
    ]

    if not matching_installations:
        raise HTTPException(status_code=404, detail=f"No installations found for user '{username}'")

    # Return just installation IDs or full installation details
    return {
        "username": username,
        "installations": [
            {
                "id": inst["id"],
                "account": inst["account"]["login"],
                "html_url": inst["html_url"],
                "target_type": inst["target_type"],
            }
            for inst in matching_installations
        ]
    }

def get_repos_services(installation_id: int):
    """
    List repositories accessible to this installation.
    """
    access_token = get_installation_access_token(installation_id)
    repo_url = "https://api.github.com/installation/repositories"
    res = requests.get(
        repo_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json"
        },
    )

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    return res.json().get("repositories", [])


def get_repo_by_id(installation_id: int, owner: str, repo: str):
    """
    Fetch metadata for a specific repository under this installation.
    """
    access_token = get_installation_access_token(installation_id)

    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    res = requests.get(
        repo_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json"
        },
    )

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    return res.json()


def post_pr_comment(pr_number: int, owner: str, repo: str, body: str, installation_id: int):
    """
    Post a general comment in the PR conversation thread.
    (This is what CodeRabbit does.)
    """
    print("Started posting comment")
    access_token = get_installation_access_token(installation_id)

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }

    res = requests.post(url, json={"body": body}, headers=headers)

    if res.status_code not in (200, 201):
        raise HTTPException(status_code=res.status_code, detail=res.text)
    
    print("Comment posted successfully")
    return res.json()


def update_pr_comment(comment_id: int, owner: str, repo: str, body: str, installation_id: int):
    """
    Update an existing PR comment with new content.
    This is used to replace the 'review in progress' comment with the final review.
    """
    print(f"Updating comment ID: {comment_id}")
    access_token = get_installation_access_token(installation_id)

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }

    res = requests.patch(url, json={"body": body}, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)
    
    print(f"Comment {comment_id} updated successfully")
    return res.json()


def delete_pr_comment(comment_id: int, owner: str, repo: str, installation_id: int):
    """
    Delete a PR comment (optional - in case you want to remove the progress comment).
    """
    access_token = get_installation_access_token(installation_id)

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }

    res = requests.delete(url, headers=headers)

    if res.status_code != 204:
        raise HTTPException(status_code=res.status_code, detail=res.text)
    
    print(f"Comment {comment_id} deleted successfully")
    return True