import json
import os
import psycopg2
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .session import engine, SessionLocal
from ..models.nurse import Nurse
from ..crud import crud_nurse
from ..schemas.nurse import NurseRegister
from ..utils.json_helpers import json_to_sql
from ..core.app_config import INSERT_MOCK_DATA  # Import the configuration flag

# Synchronous function for initializing the vector database
def init_vector_db():
    db_name = "vector_db"
    user = "postgres"
    password = "password"
    host = "pgvector-db"
    port = "5432"

    conn = psycopg2.connect(
        dbname=db_name,
        user=user,
        password=password,
        host=host,
        port=port
    )
    
    try:
        cursor = conn.cursor()

        # Begin a transaction explicitly
        cursor.execute("BEGIN;")

        # Create the vector extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Create a table with a vector column
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id BIGSERIAL PRIMARY KEY,
                embedding vector(3)
            );
        """)

        if INSERT_MOCK_DATA:  # Check if mock data should be inserted
            # Insert mock data
            cursor.execute("""
                INSERT INTO items (embedding) VALUES
                ('[0.1, 0.2, 0.3]'),
                ('[0.4, 0.5, 0.6]'),
                ('[0.7, 0.8, 0.9]');
            """)

        # Commit the transaction
        conn.commit()

    except Exception as e:
        # Rollback if there is any error
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

async def init_db():
    async with engine.begin() as conn:
        # Only create the schema without inserting mock data
        await conn.run_sync(Nurse.metadata.create_all)

    if INSERT_MOCK_DATA:  # Check if mock data should be inserted
        async with SessionLocal() as session:
            nurses = await crud_nurse.get_nurses(session)
            if not nurses:
                mock_nurses = [
                    NurseRegister(name="User1 Test", email="john.doe@example.com", password="password123"),
                    NurseRegister(name="User2 Test", email="jane.smith@example.com", password="password123"),
                    NurseRegister(name="User3 Test", email="alice.johnson@example.com", password="password123")
                ]
                for nurse in mock_nurses:
                    await crud_nurse.create_nurse(session, nurse)

            nurses = await crud_nurse.get_nurses(session)
            nurse_ids = [nurse.id for nurse in nurses]

            patients_file_path = os.path.join(os.path.dirname(__file__), '../../assets/patients.json')
            with open(patients_file_path, 'r') as file:
                patients_data = json.load(file)

            for i, patient in enumerate(patients_data["patients"]):
                patient['nurse_id'] = nurse_ids[i % len(nurse_ids)]
                patient_json = json.dumps(patient)
                await json_to_sql(session, patient_json)

async def initialize_all_databases():
    await init_db()
    init_vector_db()
