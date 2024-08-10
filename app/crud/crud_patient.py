from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List, Optional

from ..models.patient import Patient
from ..schemas.patient import PatientCreate, PatientUpdate

async def get_patient(db: AsyncSession, patient_id: int) -> Optional[Patient]:
    result = await db.execute(select(Patient).options(joinedload(Patient.nurse)).filter(Patient.id == patient_id))
    return result.scalars().unique().one_or_none()

async def get_patients(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Patient]:
    result = await db.execute(select(Patient).options(joinedload(Patient.nurse)).offset(skip).limit(limit))
    return result.scalars().unique().all()

async def get_patients_by_nurse(db: AsyncSession, nurse_id: int, skip: int = 0, limit: int = 100) -> List[Patient]:
    result = await db.execute(select(Patient).options(joinedload(Patient.nurse)).filter(Patient.nurse_id == nurse_id).offset(skip).limit(limit))
    return result.scalars().unique().all()

async def create_patient(db: AsyncSession, patient: PatientCreate) -> Patient:
    db_patient = Patient()
    for key, value in patient.model_dump().items():
        setattr(db_patient, key, value)
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)

    result = await db.execute(
        select(Patient)
        .options(joinedload(Patient.nurse))
        .where(Patient.id == db_patient.id)
    )
    db_patient = result.scalars().first()

    return db_patient

async def update_patient(db: AsyncSession, patient_id: int, patient: PatientUpdate) -> Optional[Patient]:
    db_patient = await get_patient(db, patient_id)
    if db_patient is None:
        return None
    for key, value in patient.model_dump().items():
        setattr(db_patient, key, value)
    await db.commit()
    await db.refresh(db_patient)
    return db_patient

async def delete_patient(db: AsyncSession, patient_id: int) -> bool:
    db_patient = await get_patient(db, patient_id)
    if db_patient is None:
        return False
    await db.delete(db_patient)
    await db.commit()
    return True
