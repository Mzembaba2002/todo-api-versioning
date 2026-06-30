from sqlalchemy import Column, Integer, String
from database import Base

class Tache(Base):
    __tablename__ = "taches"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, index=True)