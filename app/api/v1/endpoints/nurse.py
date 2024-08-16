from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from typing import List

from ....db.session import get_db
from ....schemas.nurse import *
from ....crud import crud_nurse

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/", response_model=List[Nurse])
async def read_nurses(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    nurses = await crud_nurse.get_nurses(db, skip=skip, limit=limit)
    return nurses

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

@router.post("/register", response_model=Nurse)
async def register_nurse(nurse: NurseRegister, db: AsyncSession = Depends(get_db)):
    if await crud_nurse.is_email_taken(db, nurse.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password before storing
    nurse.password = pwd_context.hash(nurse.password)

    return await crud_nurse.create_nurse(db, nurse)

@router.post("/login")
async def login_nurse(nurse: NurseLogin, db: AsyncSession = Depends(get_db)):
    db_nurse = await crud_nurse.get_nurse_by_email(db, nurse.email)
    if not db_nurse:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    if not pwd_context.verify(nurse.password, db_nurse.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    return {"message": "Login successful", "nurse_id": db_nurse.id}