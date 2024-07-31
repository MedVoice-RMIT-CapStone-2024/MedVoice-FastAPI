from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ....crud import crud_nurse
from ....schemas import nurse as nurse_schema
from ....db.session import get_db

router = APIRouter()

@router.post("/", response_model=nurse_schema.Nurse)
async def create_nurse(nurse: nurse_schema.NurseCreate, db: AsyncSession = Depends(get_db)):
    db_nurse = await crud_nurse.get_nurse_by_email(db, email=nurse.email)
    if db_nurse:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud_nurse.create_nurse(db=db, nurse=nurse)

@router.get("/", response_model=list[nurse_schema.Nurse])
async def read_nurses(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    nurses = await crud_nurse.get_nurses(db, skip=skip, limit=limit)
    return nurses

@router.get("/{nurse_id}", response_model=nurse_schema.Nurse)
async def read_nurse(nurse_id: int, db: AsyncSession = Depends(get_db)):
    db_nurse = await crud_nurse.get_nurse(db, nurse_id=nurse_id)
    if db_nurse is None:
        raise HTTPException(status_code=404, detail="Nurse not found")
    return db_nurse

@router.put("/{nurse_id}", response_model=nurse_schema.Nurse)
async def update_nurse(nurse_id: int, nurse: nurse_schema.NurseUpdate, db: AsyncSession = Depends(get_db)):
    db_nurse = await crud_nurse.update_nurse(db, nurse_id, nurse)
    if db_nurse is None:
        raise HTTPException(status_code=404, detail="Nurse not found")
    return db_nurse

@router.delete("/{nurse_id}", response_model=nurse_schema.Nurse)
async def delete_nurse(nurse_id: int, db: AsyncSession = Depends(get_db)):
    db_nurse = await crud_nurse.delete_nurse(db, nurse_id)
    if db_nurse is None:
        raise HTTPException(status_code=404, detail="Nurse not found")
    return db_nurse
