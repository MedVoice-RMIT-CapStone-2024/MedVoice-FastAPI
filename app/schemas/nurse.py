from pydantic import BaseModel

class NurseCreate(BaseModel):
    name: str
    email: str
    password: str

class NurseUpdate(BaseModel):
    name: str
    email: str
    password: str

class Nurse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True
