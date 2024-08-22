from pydantic import BaseModel
from typing import Optional, Dict, Any

class DemographicsOfPatient(BaseModel):
    Marital_status: Optional[str] = None
    Ethnicity: Optional[str] = None
    Occupation: Optional[str] = None

class PastMedicalHistory(BaseModel):
    Medical_history: Optional[str] = None
    Surgical_history: Optional[str] = None

class CurrentMedicationsAndDrugAllergies(BaseModel):
    Drug_allergy: Optional[str] = None
    Prescribed_medications: Optional[str] = None
    Recently_prescribed_medications: Optional[str] = None

class MentalStateExamination(BaseModel):
    Appearance_and_behavior: Optional[str] = None
    Speech_and_thoughts: Optional[str] = None
    Mood: Optional[str] = None
    Thoughts: Optional[str] = None

class PhysicalExamination(BaseModel):
    Blood_pressure: Optional[str] = None
    Pulse_rate: Optional[str] = None
    Temperature: Optional[str] = None

class PatientCreate(BaseModel):
    patient_name: str
    patient_dob: Optional[str] = None
    patient_gender: str
    demographics_of_patient: Optional[DemographicsOfPatient] = None
    past_medical_history: Optional[PastMedicalHistory] = None
    current_medications_and_drug_allergies: Optional[CurrentMedicationsAndDrugAllergies] = None
    mental_state_examination: Optional[MentalStateExamination] = None
    physical_examination: Optional[PhysicalExamination] = None
    note: Optional[str] = None
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
    patient_dob: Optional[str] = None
    patient_gender: str
    demographics_of_patient: Optional[DemographicsOfPatient] = None
    past_medical_history: Optional[PastMedicalHistory] = None
    current_medications_and_drug_allergies: Optional[CurrentMedicationsAndDrugAllergies] = None
    mental_state_examination: Optional[MentalStateExamination] = None
    physical_examination: Optional[PhysicalExamination] = None
    note: Optional[str] = None
    nurse_id: int
    nurse: Optional[NurseBase] = None

    class Config:
        orm_mode = True
