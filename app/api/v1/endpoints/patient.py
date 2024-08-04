from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ....db.session import get_db
from ....schemas.patient import Patient, PatientCreate, PatientUpdate
from ....crud import crud_patient

router = APIRouter()

# TODO: Redo READ operation

# @router.get("/", response_model=List[Patient])
# async def read_patients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
#     patients = await crud_patient.get_patients(db, skip=skip, limit=limit)
#     return patients

@router.get("/nurse/{nurse_id}", response_model=List[Patient])
async def read_patients_by_nurse(nurse_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    patients = await crud_patient.get_patients_by_nurse(db, nurse_id=nurse_id, skip=skip, limit=limit)
    return patients

@router.post("/", response_model=Patient)
async def create_patient(patient: PatientCreate, db: AsyncSession = Depends(get_db)):
    return await crud_patient.create_patient(db, patient)

# TODO: Redo READ operation

# @router.get("/{patient_id}", response_model=Patient)
# async def read_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
#     db_patient = await crud_patient.get_patient(db, patient_id)
#     if db_patient is None:
#         raise HTTPException(status_code=404, detail="Patient not found")
#     return db_patient

@router.put("/{patient_id}", response_model=Patient)
async def update_patient(patient_id: int, patient: PatientUpdate, db: AsyncSession = Depends(get_db)):
    db_patient = await crud_patient.update_patient(db, patient_id, patient)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.delete("/{patient_id}", response_model=bool)
async def delete_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_patient.delete_patient(db, patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return success
