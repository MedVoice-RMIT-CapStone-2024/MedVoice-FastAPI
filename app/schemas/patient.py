from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any

class StringField(BaseModel):
    type: str = Field(default="string")
    value: str

    def __str__(self):
        return self.value

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, dict) and "value" in value:
            return value["value"]
        raise ValueError("Invalid format for StringField")

class DemographicsOfPatient(BaseModel):
    Marital_status: Optional[StringField] = None
    Ethnicity: Optional[StringField] = None
    Occupation: Optional[StringField] = None

class PastMedicalHistory(BaseModel):
    Medical_history: Optional[StringField] = None
    Surgical_history: Optional[StringField] = None

class CurrentMedicationsAndDrugAllergies(BaseModel):
    Drug_allergy: Optional[StringField] = None
    Prescribed_medications: Optional[StringField] = None
    Recently_prescribed_medications: Optional[StringField] = None

class MentalStateExamination(BaseModel):
    Appearance_and_behavior: Optional[StringField] = None
    Speech_and_thoughts: Optional[StringField] = None
    Mood: Optional[StringField] = None
    Thoughts: Optional[StringField] = None

class PhysicalExamination(BaseModel):
    Blood_pressure: Optional[StringField] = None
    Pulse_rate: Optional[StringField] = None
    Temperature: Optional[StringField] = None

class PatientCreate(BaseModel):
    patient_name: StringField
    patient_dob: Optional[StringField] = None
    patient_gender: StringField
    demographics_of_patient: Optional[DemographicsOfPatient] = None
    past_medical_history: Optional[PastMedicalHistory] = None
    current_medications_and_drug_allergies: Optional[CurrentMedicationsAndDrugAllergies] = None
    mental_state_examination: Optional[MentalStateExamination] = None
    physical_examination: Optional[PhysicalExamination] = None
    note: Optional[StringField] = None
    nurse_id: int

    class Config:
        orm_mode = True

    @validator('patient_name', 'patient_dob', 'patient_gender', 'note', pre=True, each_item=True)
    def extract_value(cls, v):
        if isinstance(v, dict) and "value" in v:
            return v["value"]
        return v

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
