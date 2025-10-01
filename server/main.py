from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db.database import init_db
from servcies.github import get_installations_service, get_repos_services

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/installations")
def get_installation():
    return {"installations": get_installations_service()}

@app.get("/repos")
def get_repos(installation_id: int = Query(...)):
    return {"repositories": get_repos_services(installation_id)}
