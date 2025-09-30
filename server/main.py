from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests,jwt,time,os
from utils.generate_app_jwt import get_installations_headers
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/installations")
def get_installations():
    url = "https://api.github.com/app/installations"
    headers=get_installations_headers()
    res=requests.get(url,headers=headers)
    
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)
    data=res.json()
    # Return relevant info to frontend
    installations = [
        {
            "id": inst["id"],
            "account": inst["account"],
            "app_slug": inst.get("app_slug", "")
        } for inst in data
    ]
    return {"installations": installations}


@app.get("/repos")
def get_repos(installation_id: int = Query(...)):
    """
    Fetch repositories for a specific installation
    """
    # 1️⃣ Generate installation token
    token_url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = get_installations_headers()
    token_res = requests.post(token_url, headers=headers)

    if token_res.status_code != 201:
        raise HTTPException(status_code=token_res.status_code, detail=token_res.text)

    token_data = token_res.json()
    access_token = token_data["token"]

    # 2️⃣ Fetch repos
    repo_url = "https://api.github.com/installation/repositories"
    repo_res = requests.get(repo_url, headers={
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github+json"
    })

    if repo_res.status_code != 200:
        raise HTTPException(status_code=repo_res.status_code, detail=repo_res.text)

    repos = repo_res.json().get("repositories", [])
    return {"repositories": repos}