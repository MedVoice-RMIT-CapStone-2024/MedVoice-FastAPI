from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.nurse import Nurse
from ..schemas.nurse import NurseCreate, NurseUpdate

async def create_nurse(db: AsyncSession, nurse: NurseCreate):
    db_nurse = await get_nurse_by_email(db, nurse.email)
    if db_nurse:
        return None
    new_nurse = Nurse(name=nurse.name, email=nurse.email, password=nurse.password)
    db.add(new_nurse)
    await db.commit()
    await db.refresh(new_nurse)
    return new_nurse

async def get_nurses(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Nurse).offset(skip).limit(limit))
    return result.scalars().all()

async def get_nurse(db: AsyncSession, nurse_id: int):
    result = await db.execute(select(Nurse).where(Nurse.id == nurse_id))
    return result.scalar_one_or_none()

async def get_nurse_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(Nurse).where(Nurse.email == email))
    return result.scalar_one_or_none()

async def update_nurse(db: AsyncSession, nurse_id: int, nurse: NurseUpdate):
    db_nurse = await get_nurse(db, nurse_id)
    if db_nurse:
        db_nurse.name = nurse.name
        db_nurse.email = nurse.email
        db_nurse.password = nurse.password
        await db.commit()
        await db.refresh(db_nurse)
        return db_nurse
    return None

async def delete_nurse(db: AsyncSession, nurse_id: int):
    db_nurse = await get_nurse(db, nurse_id)
    if db_nurse:
        await db.delete(db_nurse)
        await db.commit()
        return db_nurse
    return None
