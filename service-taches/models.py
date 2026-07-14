from sqlalchemy import Column, Integer, String
from database import Base


class Tache(Base):
    __tablename__ = "taches"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, index=True)
    # On stocke seulement l'ID de la catégorie (pas de clé étrangère SQL :
    # la catégorie vit dans une AUTRE base, gérée par un AUTRE service)
    categorie_id = Column(Integer, nullable=True)
