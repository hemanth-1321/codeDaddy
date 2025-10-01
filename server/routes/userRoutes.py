from fastapi import APIRouter,Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from db.database import get_session
from db.models import User
from sqlmodel import select
from datetime import datetime

router=APIRouter()



@router.post("/log_user")
async def upsert_user(user_data:dict,session:AsyncSession=Depends(get_session)):
    stmt=select(User).where(User.github_user_id==user_data["github_user_id"])
    existing_user=await session.exec(stmt)
    user=existing_user.first()
    
    if user:
        user.name=user_data.get("name")
        user.avatar_url=user_data.get("avatar_url")
        session.add(user)
        
    else:
        user=User(
            github_user_id=user_data["github_user_id"],
            name=user_data.get("name"),
            avatar_url=user_data.get("avatar_url"),
        )
        session.add(user)
    await session.commit()
    
    return{
        "status":"ok",
        "user":user.github_user_id
    }