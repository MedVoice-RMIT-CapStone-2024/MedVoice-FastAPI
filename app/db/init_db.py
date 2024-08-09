import json
import os
import psycopg2

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .session import engine, SessionLocal
from ..models.nurse import Nurse
from ..models.patient import Patient
from ..crud import crud_nurse, crud_patient
from ..schemas.nurse import NurseCreate
from ..utils.json_to_sql import json_to_sql

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
    conn.autocommit = True

    cursor = conn.cursor()

    # Create the vector extension
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create a table with a vector column
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id BIGSERIAL PRIMARY KEY,
            embedding vector(3)
        );
    """)

    # Insert mock data
    cursor.execute("""
        INSERT INTO items (embedding) VALUES
        ('[0.1, 0.2, 0.3]'),
        ('[0.4, 0.5, 0.6]'),
        ('[0.7, 0.8, 0.9]');
    """)

    cursor.close()
    conn.close()


# Asynchronous function for initializing the main database
async def init_db():
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Nurse.metadata.drop_all)
        await conn.run_sync(Patient.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Nurse.metadata.create_all)
        await conn.run_sync(Patient.metadata.create_all)

    async with SessionLocal() as session:
        # Initialize Nurses
        nurses = await crud_nurse.get_nurses(session)
        if not nurses:
            mock_nurses = [
                NurseCreate(name="John Doe", email="john.doe@example.com", password="password123"),
                NurseCreate(name="Jane Smith", email="jane.smith@example.com", password="password123"),
                NurseCreate(name="Alice Johnson", email="alice.johnson@example.com", password="password123")
            ]
            for nurse in mock_nurses:
                await crud_nurse.create_nurse(session, nurse)

        # Fetch the created nurses to use their IDs
        nurses = await crud_nurse.get_nurses(session)
        nurse_ids = [nurse.id for nurse in nurses]

        # Initialize Patients from JSON file
        patients_file_path = os.path.join(os.path.dirname(__file__), '../../assets/patients.json')
        with open(patients_file_path, 'r') as file:
            patients_data = json.load(file)

        # Assign nurse_id to each patient
        for i, patient in enumerate(patients_data["patients"]):
            patient['nurse_id'] = nurse_ids[i % len(nurse_ids)]
            patient_json = json.dumps(patient)
            await json_to_sql(session, patient_json)


# Function to initialize both databases
async def initialize_all_databases():
    # Initialize the main database asynchronously
    await init_db()

    # Initialize the vector database synchronously
    init_vector_db()