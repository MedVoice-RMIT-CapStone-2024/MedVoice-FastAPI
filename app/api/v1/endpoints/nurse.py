from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from typing import List, Union, Dict

from ....db.session import get_db
from ....schemas.nurse import *
from ....crud import crud_nurse

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/", response_model=Union[List[Nurse], Dict[str, str]])
async def read_nurses(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)) -> Union[List[Nurse], Dict[str, str]]:
    nurses = await crud_nurse.get_nurses(db, skip=skip, limit=limit)
    if nurses:
        return nurses
    return {"detail": "No nurses found"}  # Return detail message if nurses are not found

@router.get("/{nurse_id}", response_model=Union[Nurse, Dict[str, str]])
async def read_nurse(nurse_id: int, db: AsyncSession = Depends(get_db)) -> Union[Nurse, Dict[str, str]]:
    db_nurse = await crud_nurse.get_nurse(db, nurse_id)
    if db_nurse:
        return db_nurse
    return {"detail": "Nurse not found"}  # Return detail message if the nurse is not found

@router.put("/{nurse_id}", response_model=Union[Nurse, Dict[str, str]])
async def update_nurse(nurse_id: int, nurse: NurseUpdate, db: AsyncSession = Depends(get_db)) -> Union[Nurse, Dict[str, str]]:
    db_nurse = await crud_nurse.update_nurse(db, nurse_id, nurse)
    if db_nurse:
        return db_nurse
    return {"detail": "Nurse not found or update failed"}  # Return detail message if the nurse is not found or update fails

@router.delete("/{nurse_id}", response_model=Union[bool, Dict[str, str]])
async def delete_nurse(nurse_id: int, db: AsyncSession = Depends(get_db)) -> Union[bool, Dict[str, str]]:
    success = await crud_nurse.delete_nurse(db, nurse_id)
    if success:
        return success
    return {"detail": "Nurse not found or delete operation failed"}  # Return detail message if the delete operation fails

@router.post("/register", response_model=Union[Nurse, Dict[str, str]])
async def register_nurse(nurse: NurseRegister, db: AsyncSession = Depends(get_db)) -> Union[Nurse, Dict[str, str]]:
    if await crud_nurse.is_email_taken(db, nurse.email):
        return {"detail": "Email already registered"}  # Return detail message if the email is already taken

    # Hash the password before storing
    nurse.password = pwd_context.hash(nurse.password)

    created_nurse = await crud_nurse.create_nurse(db, nurse)
    if created_nurse:
        return created_nurse
    return {"detail": "Nurse registration failed"}  # Return detail message if nurse creation fails

@router.post("/login", response_model=Dict[str, Union[str, int]])
async def login_nurse(nurse: NurseLogin, db: AsyncSession = Depends(get_db)) -> Dict[str, Union[str, int]]:
    db_nurse = await crud_nurse.get_nurse_by_email(db, nurse.email)
    if not db_nurse or not pwd_context.verify(nurse.password, db_nurse.password):
        return {"detail": "Invalid email or password"}  # Return detail message if email or password is incorrect

    return {"message": "Login successful", "nurse_id": db_nurse.id}
