import json
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.patient import PatientCreate
from ..crud.crud_patient import create_patient

async def json_to_sql(db: AsyncSession, patient_json: str):
    patient_dict = json.loads(patient_json)
    patient_create = PatientCreate(**patient_dict)
    return await create_patient(db, patient_create)
