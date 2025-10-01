from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from db.database import get_session
from db.models import Repository
from sqlmodel import select

router = APIRouter()

@router.post("/select")
async def select_repo(repo_data: dict, session: AsyncSession = Depends(get_session)):
    github_repo_id = repo_data["github_repo_id"]
    installation_id = repo_data["installation_id"]

    stmt = select(Repository).where(Repository.github_repo_id == github_repo_id)
    result = await session.execute(stmt)  
    repo = result.scalar_one_or_none()  # Fixed: use scalar_one_or_none()

    if repo:
        repo.installation_id = installation_id
        repo.is_active = True
        session.add(repo)
    else:
        repo = Repository(
            github_repo_id=github_repo_id,
            full_name=repo_data.get("full_name", "Unknown"),
            installation_id=installation_id,
            is_active=True,
        )
        session.add(repo)

    await session.commit()
    await session.refresh(repo)  # Get the updated object with DB defaults
    return {"status": "ok", "repo_id": repo.github_repo_id}