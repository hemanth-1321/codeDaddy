from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime,timezone

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    github_user_id: int = Field(sa_column_kwargs={"unique": True})
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at:datetime=Field(default_factory=lambda:datetime.now())
    

class Repository(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    github_repo_id: int = Field(sa_column_kwargs={"unique": True})
    full_name: str
    installation_id: int 
    is_active: bool = Field(default=True)
    
    
    created_at:datetime=Field(default_factory=lambda:datetime.now())
    
    