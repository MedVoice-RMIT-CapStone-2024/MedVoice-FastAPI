from pydantic import BaseModel
from typing import List, Optional

class NurseBase(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

class NurseCreate(BaseModel):
    name: str
    email: str
    password: str

class NurseUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    password: Optional[str]

class Nurse(NurseBase):
    patients: List["Patient"] = []

from .patient import Patient  # Avoid circular import issues
Nurse.update_forward_refs()