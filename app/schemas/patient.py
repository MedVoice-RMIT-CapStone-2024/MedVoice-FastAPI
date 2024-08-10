from pydantic import BaseModel
from typing import List, Optional

class MedicalDiagnosis(BaseModel):
    name: str

class MedicalTreatment(BaseModel):
    name: str
    prescription: Optional[str] = None

class HealthVital(BaseModel):
    status: str
    value: Optional[str] = None
    units: Optional[str] = None

class PatientCreate(BaseModel):
    patient_name: str
    patient_age: int
    patient_gender: str
    medical_diagnosis: List[MedicalDiagnosis]
    medical_treatment: List[MedicalTreatment]
    health_vital: List[HealthVital]
    nurse_id: int

class PatientUpdate(PatientCreate):
    pass

class NurseBase(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

class Patient(BaseModel):
    id: int
    patient_name: str
    patient_age: int
    patient_gender: str
    medical_diagnosis: List[MedicalDiagnosis]
    medical_treatment: List[MedicalTreatment]
    health_vital: List[HealthVital]
    nurse_id: int
    nurse: Optional[NurseBase] = None

    class Config:
        orm_mode = True
