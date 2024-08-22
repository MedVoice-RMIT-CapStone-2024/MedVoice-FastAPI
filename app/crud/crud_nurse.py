from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from typing import List, Optional

from ..models.nurse import Nurse
from ..schemas.nurse import NurseRegister, NurseUpdate

async def get_nurse(db: AsyncSession, nurse_id: int) -> Optional[Nurse]:
    result = await db.execute(select(Nurse).options(joinedload(Nurse.patients)).filter(Nurse.id == nurse_id))
    return result.scalars().unique().one_or_none()

async def get_nurses(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Nurse]:
    result = await db.execute(select(Nurse).options(joinedload(Nurse.patients)).offset(skip).limit(limit))
    return result.scalars().unique().all()

async def create_nurse(db: AsyncSession, nurse: NurseRegister) -> Nurse:
    db_nurse = Nurse()
    for key, value in nurse.model_dump().items():
        setattr(db_nurse, key, value)
    db.add(db_nurse)
    await db.commit()
    await db.refresh(db_nurse)

    result = await db.execute(
        select(Nurse)
        .options(joinedload(Nurse.patients))
        .where(Nurse.id == db_nurse.id)
    )
    db_nurse = result.scalars().first()

    return db_nurse

async def update_nurse(db: AsyncSession, nurse_id: int, nurse: NurseUpdate) -> Optional[Nurse]:
    db_nurse = await get_nurse(db, nurse_id)
    if db_nurse is None:
        return None
    for key, value in nurse.model_dump().items():
        if value is not None:
            setattr(db_nurse, key, value)
    await db.commit()
    await db.refresh(db_nurse)
    return db_nurse

async def delete_nurse(db: AsyncSession, nurse_id: int) -> bool:
    db_nurse = await get_nurse(db, nurse_id)
    if db_nurse is None:
        return False
    await db.delete(db_nurse)
    await db.commit()
    return True

async def is_email_taken(db: AsyncSession, email: str) -> bool:
    result = await db.execute(select(Nurse).filter(Nurse.email == email))
    return result.scalars().unique().one_or_none() is not None

async def get_nurse_by_email(db: AsyncSession, email: str) -> Optional[Nurse]:
    result = await db.execute(select(Nurse).filter(Nurse.email == email))
    return result.scalars().unique().one_or_none()
