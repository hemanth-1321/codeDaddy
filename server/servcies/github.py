import requests

from fastapi import HTTPException
from utils.generate_app_jwt import get_installations_headers

def get_installations_service():
    url = "https://api.github.com/app/installations"
    headers=get_installations_headers()
    res=requests.get(url,headers=headers)
    
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)
    data=res.json()
    installations = [
        {   
            "id": inst["id"],
            "account": inst["account"],
            "app_slug": inst.get("app_slug", "")
        } for inst in data
    ]
    return  installations

def get_repos_services(installation_id: int):
    token_url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = get_installations_headers()
    token_response = requests.post(token_url, headers=headers)
    token_response.raise_for_status()

    access_token = token_response.json()["token"]

    repo_url = "https://api.github.com/installation/repositories"
    repo_res = requests.get(repo_url, headers={
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github+json"
    })
    repo_res.raise_for_status()

    return repo_res.json().get("repositories", [])




def get_repo_by_id(installation_id: int, owner: str, repo: str):
    
    token_url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = get_installations_headers() 
    token_response = requests.post(token_url, headers=headers)

    if token_response.status_code != 201:
        raise HTTPException(status_code=token_response.status_code, detail=token_response.text)

    access_token = token_response.json()["token"]

    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    repo_res = requests.get(
        repo_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
    )

    if repo_res.status_code != 200:
        raise HTTPException(status_code=repo_res.status_code, detail=repo_res.text)

    return repo_res.json()