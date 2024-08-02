from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from ..models.embedding import Embedding
from ..schemas.embedding import EmbeddingCreate, EmbeddingUpdate

class CRUDEmbedding:
    async def create_embedding(self, db: AsyncSession, embedding_create: EmbeddingCreate):
        db_embedding = Embedding(
            document_id=embedding_create.document_id,
            content=embedding_create.content,
            embedding=embedding_create.embedding
        )
        db.add(db_embedding)
        await db.commit()
        await db.refresh(db_embedding)
        return db_embedding

    async def get_embedding(self, db: AsyncSession, document_id: str):
        result = await db.execute(select(Embedding).filter(Embedding.document_id == document_id))
        return result.scalar_one_or_none()

    async def update_embedding(self, db: AsyncSession, document_id: str, embedding_update: EmbeddingUpdate):
        await db.execute(
            update(Embedding)
            .where(Embedding.document_id == document_id)
            .values(
                content=embedding_update.content,
                embedding=embedding_update.embedding
            )
        )
        await db.commit()

    async def delete_embedding(self, db: AsyncSession, document_id: str):
        await db.execute(
            delete(Embedding).where(Embedding.document_id == document_id)
        )
        await db.commit()

crud_embedding = CRUDEmbedding()
