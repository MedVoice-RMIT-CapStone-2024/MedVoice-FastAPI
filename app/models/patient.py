from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    patient_dob = Column(String)  # Assuming date of birth as string
    patient_gender = Column(String)

    demographics_of_patient = Column(JSON)  # JSON field to store Marital_status, Ethnicity, Occupation
    past_medical_history = Column(JSON)  # JSON field to store Medical_history, Surgical_history
    current_medications_and_drug_allergies = Column(JSON)  # JSON field for Drug_allergy, Prescribed_medications, Recently_prescribed_medications
    mental_state_examination = Column(JSON)  # JSON field for mental state examination details
    physical_examination = Column(JSON)  # JSON field for physical examination details
    note = Column(String)  # Note field for additional comments

    nurse_id = Column(Integer, ForeignKey('nurses.id'))

    nurse = relationship("Nurse", back_populates="patients", lazy="joined")
