from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    patient_age = Column(Integer)
    patient_gender = Column(String)
    medical_diagnosis = Column(JSON)
    medical_treatment = Column(JSON)
    health_vital = Column(JSON)
    nurse_id = Column(Integer, ForeignKey('nurses.id'))

    nurse = relationship("Nurse", back_populates="patients", lazy="joined")
