from pydantic import BaseModel
from typing import Optional

class NurseBase(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class NurseRegister(BaseModel):
    name: str
    email: str
    password: str

class NurseLogin(BaseModel):
    email: str
    password: str

class NurseUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]

class Nurse(NurseBase):
    pass
