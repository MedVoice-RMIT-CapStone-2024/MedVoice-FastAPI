from pydantic import BaseModel
from uuid import UUID

class EmbeddingCreate(BaseModel):
    document_id: UUID
    content: str
    embedding: list[float]

class EmbeddingUpdate(BaseModel):
    content: str
    embedding: list[float]

class Embedding(BaseModel):
    id: int
    document_id: UUID
    content: str
    embedding: list[float]

    class Config:
        from_attributes = True
