from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from server.routes.webhook import router as webhook_router
from server.servcies.github import get_installations_service, get_repos_services,get_repo_by_id

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(webhook_router,prefix="/api/v1/webhook",tags=["webhook"])

@app.get("/installations")
def get_installation():
    return {"installations": get_installations_service()}

@app.get("/repos")
def get_repos(installation_id: int = Query(...)):
    return {"repositories": get_repos_services(installation_id)}

@app.get("/repo/{repo}")
def get_repo(repo: str, installation_id: int    = Query(...), owner: str = Query(...)):
    return get_repo_by_id(installation_id, owner, repo)



