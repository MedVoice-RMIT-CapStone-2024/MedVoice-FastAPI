import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .session import engine
from ..models.nurse import Nurse
from ..models.embedding import Embedding
from ..core.db_config import settings
from pgvector.asyncpg import register_vector

def get_asyncpg_dsn(sqlalchemy_dsn: str) -> str:
    print("Getting asyncpg DSN")
    if sqlalchemy_dsn.startswith("postgresql+asyncpg://"):
        return sqlalchemy_dsn.replace("postgresql+asyncpg://", "postgresql://")
    return sqlalchemy_dsn

async def create_extensions():
    print("Creating extensions")
    asyncpg_dsn = get_asyncpg_dsn(settings.DATABASE_URL)
    conn = await asyncpg.connect(asyncpg_dsn)
    try:
        print("Executing CREATE EXTENSION IF NOT EXISTS vector")
        await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
        print("Registering vector")
        await register_vector(conn)
    finally:
        print("Closing connection")
        await conn.close()

async def create_schemas_and_tables():
    print("Creating schemas and tables")
    async with engine.begin() as conn:
        print("Dropping and creating schemas")
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("DROP SCHEMA IF EXISTS nurses CASCADE")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("DROP SCHEMA IF EXISTS embeddings CASCADE")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("CREATE SCHEMA nurses")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("CREATE SCHEMA embeddings")))

        print("Creating tables")
        await conn.run_sync(Nurse.metadata.create_all)
        await conn.run_sync(Embedding.metadata.create_all)

async def init_db():
    print("Initializing database")
    await create_extensions()
    await create_schemas_and_tables()

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
