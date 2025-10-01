import ssl
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from utils.config import DATABASE_URL

# Convert sync URL to async URL
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set. Please check your configuration.")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create SSL context (required for Neon)
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = True
ssl_ctx.verify_mode = ssl.CERT_REQUIRED

# Create engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    connect_args={"ssl": ssl_ctx},
    echo=True,  # set to False in prod
)

# Session factory
async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

# Dependency for FastAPI routes
async def get_session():
    async with async_session() as session:
        yield session

# Initialize DB (create tables)
async def init_db():
    import db.models 

    print("Tables in metadata:", SQLModel.metadata.tables.keys())
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
