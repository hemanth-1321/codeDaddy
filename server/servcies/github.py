import requests
from fastapi import HTTPException
from server.utils.generate_app_jwt import get_installations_headers


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


def get_installations_service():
    """
    List all installations for this GitHub App.
    """
    url = "https://api.github.com/app/installations"
    headers = get_installations_headers()
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    data = res.json()
    return [
        {
            "id": inst["id"],
            "account": inst["account"],
            "app_slug": inst.get("app_slug", "")
        }
        for inst in data
    ]


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
    print("started posting comment")
    access_token = get_installation_access_token(installation_id)

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }

    res = requests.post(url, json={"body": body}, headers=headers)

    if res.status_code not in (200, 201):
        raise HTTPException(status_code=res.status_code, detail=res.text)
    print("completed")
    return res.json()
