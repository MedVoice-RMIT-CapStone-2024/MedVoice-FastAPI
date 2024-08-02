from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .session import engine, SessionLocal
from ..models.nurse import Nurse
from ..models.embedding import Embedding
from ..crud import crud_nurse, crud_embedding
from ..schemas.nurse import NurseCreate
from ..schemas.embedding import EmbeddingCreate
from pgvector.asyncpg import register_vector
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from ..core.db_config import settings
import numpy as np
import json
from uuid import uuid4

async def init_db():
    async with engine.begin() as conn:
        # Drop and re-create the schemas
        await conn.execute(text("DROP SCHEMA IF EXISTS nurses CASCADE"))
        await conn.execute(text("DROP SCHEMA IF EXISTS embeddings CASCADE"))
        await conn.execute(text("CREATE SCHEMA nurses"))
        await conn.execute(text("CREATE SCHEMA embeddings"))

        # Enable vector extension
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))

    async with SessionLocal() as session:
        # Register vector type
        async with session.begin():
            conn = await session.connection()
            raw_conn = conn.connection.raw_connection()
            await register_vector(raw_conn)

        # Create the nurses table
        await session.execute(text("""
        CREATE TABLE IF NOT EXISTS nurses.nurses (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(100)
        )
        """))

        # Create the embeddings table
        await session.execute(text("""
        CREATE TABLE IF NOT EXISTS embeddings.documents (
            id SERIAL PRIMARY KEY,
            document_id UUID,
            content TEXT,
            embedding vector(1536) -- Change size according to your embedding size
        )
        """))

        # Create vector index
        await session.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_embeddings_embedding
        ON embeddings.documents USING ivfflat (embedding vector_l2_ops)
        WITH (lists = 100)
        """))

        # Initialize nurses table with mock data
        await init_nurses(session)

        # Initialize vector database for embeddings
        await init_vector_db(session)

async def init_nurses(session: AsyncSession):
    # Check if the nurses table is empty
    nurses = await crud_nurse.get_nurses(session)
    if not nurses:
        # Insert mock data
        mock_nurses = [
            NurseCreate(name="John Doe", email="john.doe@example.com", password="password123"),
            NurseCreate(name="Jane Smith", email="jane.smith@example.com", password="password123"),
            NurseCreate(name="Alice Johnson", email="alice.johnson@example.com", password="password123")
        ]

        for nurse in mock_nurses:
            await crud_nurse.create_nurse(session, nurse)

async def init_vector_db(session: AsyncSession):
    # Load and process example documents for embeddings
    with open("assets/patients.json", "r") as file:
        patients_data = json.load(file)["patients"]

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
    all_splits = text_splitter.split_documents(patients_data)

    embedding = OllamaEmbeddings(base_url="http://ollama:11434", model="nomic-embed-text")
    vectorstore = PGVector.from_documents(
        documents=all_splits,
        embedding=embedding,
        collection_name="embeddings.documents",
        connection_string=settings.DATABASE_URL
    )

    # Insert mock embeddings
    for doc, vec in zip(all_splits, vectorstore.embeddings):
        embedding_create = EmbeddingCreate(
            document_id=uuid4(),
            content=json.dumps(doc),
            embedding=np.array(vec).tolist()  # Convert numpy array to list for JSON serialization
        )
        await crud_embedding.create_embedding(session, embedding_create)

    # Print message to confirm vector database initialization
    print("Vector database initialized with sample documents")
