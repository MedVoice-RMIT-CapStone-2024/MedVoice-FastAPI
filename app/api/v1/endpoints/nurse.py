from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ....db.session import get_db
from ....schemas.nurse import Nurse, NurseCreate, NurseUpdate
from ....crud import crud_nurse

router = APIRouter()

@router.get("/", response_model=List[Nurse])
async def read_nurses(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    nurses = await crud_nurse.get_nurses(db, skip=skip, limit=limit)
    return nurses

@router.post("/", response_model=Nurse)
async def create_nurse(nurse: NurseCreate, db: AsyncSession = Depends(get_db)):
    if await crud_nurse.is_email_taken(db, nurse.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud_nurse.create_nurse(db, nurse)

@router.get("/{nurse_id}", response_model=Nurse)
async def read_nurse(nurse_id: int, db: AsyncSession = Depends(get_db)):
    db_nurse = await crud_nurse.get_nurse(db, nurse_id)
    if db_nurse is None:
        raise HTTPException(status_code=404, detail="Nurse not found")
    return db_nurse

@router.put("/{nurse_id}", response_model=Nurse)
async def update_nurse(nurse_id: int, nurse: NurseUpdate, db: AsyncSession = Depends(get_db)):
    db_nurse = await crud_nurse.update_nurse(db, nurse_id, nurse)
    if db_nurse is None:
        raise HTTPException(status_code=404, detail="Nurse not found")
    return db_nurse

@router.delete("/{nurse_id}", response_model=bool)
async def delete_nurse(nurse_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_nurse.delete_nurse(db, nurse_id)
    if not success:
        raise HTTPException(status_code=404, detail="Nurse not found")
    return success
