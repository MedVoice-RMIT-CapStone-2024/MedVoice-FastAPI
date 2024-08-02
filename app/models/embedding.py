from sqlalchemy import Column, Integer, String, Text, Sequence
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Embedding(Base):
    __tablename__ = "documents"
    __table_args__ = {'schema': 'embeddings'}

    id = Column(Integer, Sequence('embedding_id_seq'), primary_key=True, index=True)
    document_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # Assuming VECTOR type is not natively supported by SQLAlchemy
