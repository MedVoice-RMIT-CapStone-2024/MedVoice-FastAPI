from sqlalchemy import Column, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Embedding(Base):
    __tablename__ = "documents"
    __table_args__ = {'schema': 'embeddings'}

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)  # Adjust the dimension size according to your embedding
