from pydantic import BaseModel
from uuid import UUID

class EmbeddingCreate(BaseModel):
    document_id: UUID
    content: str
    embedding: str

class EmbeddingUpdate(BaseModel):
    content: str
    embedding: str

class Embedding(BaseModel):
    id: int
    document_id: UUID
    content: str
    embedding: str

    class Config:
        orm_mode = True
