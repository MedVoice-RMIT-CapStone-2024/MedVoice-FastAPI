from sqlalchemy.ext.asyncio import AsyncSession
from .session import engine, SessionLocal
from ..models.nurse import Nurse
from ..crud import crud_nurse
from ..schemas.nurse import NurseCreate

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Nurse.metadata.create_all)

    async with SessionLocal() as session:
        # Check if the table is empty
        nurses = await crud_nurse.get_nurses(session)
        if not nurses:
            # Insert mock data
            mock_nurses = [
                NurseCreate(name="John Doe", email="john.doe@example.com", password="password123"),
                NurseCreate(name="Jane Smith", email="jane.smith@example.com", password="password123"),
                NurseCreate(name="Alice Johnson", email="alice.johnson@example.com", password="password123")
            ]

            for nurse in mock_nurses:
                await crud_nurse.create_nurse(session, nurse)
