from pydantic import BaseModel

class TacheBase(BaseModel):
    titre: str

class TacheCreate(TacheBase):
    pass

class TacheResponse(TacheBase):
    id: int

    class Config:
        from_attributes = True