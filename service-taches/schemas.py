from pydantic import BaseModel
from typing import Optional


class TacheBase(BaseModel):
    titre: str
    categorie_id: Optional[int] = None


class TacheCreate(TacheBase):
    pass


class TacheResponse(TacheBase):
    id: int
    categorie_verifiee: Optional[bool] = None  # info ajoutée par l'API, pas stockée en base

    class Config:
        from_attributes = True
