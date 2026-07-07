from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

import models
import schemas
from database import engine, SessionLocal

load_dotenv()

PORT = os.getenv("PORT", "8000")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API To-Do", version="1.0.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def accueil():
    return {"message": "Bienvenue sur l'API To-Do"}


@app.post("/api/v1/taches", response_model=schemas.TacheResponse, status_code=status.HTTP_201_CREATED)
def creer_tache(tache: schemas.TacheCreate, db: Session = Depends(get_db)):
    nouvelle_tache = models.Tache(titre=tache.titre)
    db.add(nouvelle_tache)
    db.commit()
    db.refresh(nouvelle_tache)
    print("Nouvelle tâche créée :", nouvelle_tache.titre)
    return nouvelle_tache


@app.get("/api/v1/taches", response_model=list[schemas.TacheResponse])
def lire_taches(db: Session = Depends(get_db)):
    return db.query(models.Tache).all()


@app.get("/api/v1/taches/{tache_id}", response_model=schemas.TacheResponse)
def lire_tache(tache_id: int, db: Session = Depends(get_db)):
    tache = db.query(models.Tache).filter(models.Tache.id == tache_id).first()
    if tache is None:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    return tache


@app.put("/api/v1/taches/{tache_id}", response_model=schemas.TacheResponse)
def modifier_tache(tache_id: int, tache_update: schemas.TacheCreate, db: Session = Depends(get_db)):
    tache = db.query(models.Tache).filter(models.Tache.id == tache_id).first()
    if tache is None:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")

    tache.titre = tache_update.titre
    db.commit()
    db.refresh(tache)'e
    print("Tâche modifiée :", tache.titre)
    return tache


@app.delete("/api/v1/taches/{tache_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_tache(tache_id: int, db: Session = Depends(get_db)):
    tache = db.query(models.Tache).filter(models.Tache.id == tache_id).first()
    if tache is None:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")

    db.delete(tache)
    db.commit()
    print("Tâche supprimée :", tache_id)
    return None 
@app.get("/")
def accueil():
    return {"message": "Bienvenue sur l'API To-Do"}

@app.get("/health")
def health():
    return {
        "status": "OK",
        "message": "API opérationnelle"
    }
@app.get("/version")
def version():
    return {
        "version": "1.0.0",
        "author": "Mzembaba"
    }
