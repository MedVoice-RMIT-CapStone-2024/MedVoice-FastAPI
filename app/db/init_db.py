import json
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .session import engine, SessionLocal
from ..models.nurse import Nurse
from ..models.patient import Patient
from ..crud import crud_nurse, crud_patient
from ..schemas.nurse import NurseCreate
from ..utils.json_to_sql import json_to_sql

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
