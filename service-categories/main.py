from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

import models
import schemas
from database import engine, SessionLocal

load_dotenv()
PORT = os.getenv("PORT", "8001")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Service Catégories", version="1.0.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def accueil():
    return {"message": "Bienvenue sur le service Catégories"}


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "service-categories",
        "message": "Service opérationnel"
    }


@app.post("/api/v1/categories", response_model=schemas.CategorieResponse, status_code=status.HTTP_201_CREATED)
def creer_categorie(categorie: schemas.CategorieCreate, db: Session = Depends(get_db)):
    existe = db.query(models.Categorie).filter(models.Categorie.nom == categorie.nom).first()
    if existe:
        raise HTTPException(status_code=400, detail="Cette catégorie existe déjà")

    nouvelle_categorie = models.Categorie(nom=categorie.nom)
    db.add(nouvelle_categorie)
    db.commit()
    db.refresh(nouvelle_categorie)
    print("Nouvelle catégorie créée :", nouvelle_categorie.nom)
    return nouvelle_categorie


@app.get("/api/v1/categories", response_model=list[schemas.CategorieResponse])
def lire_categories(db: Session = Depends(get_db)):
    return db.query(models.Categorie).all()


@app.get("/api/v1/categories/{categorie_id}", response_model=schemas.CategorieResponse)
def lire_categorie(categorie_id: int, db: Session = Depends(get_db)):
    categorie = db.query(models.Categorie).filter(models.Categorie.id == categorie_id).first()
    if categorie is None:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return categorie


@app.delete("/api/v1/categories/{categorie_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_categorie(categorie_id: int, db: Session = Depends(get_db)):
    categorie = db.query(models.Categorie).filter(models.Categorie.id == categorie_id).first()
    if categorie is None:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    db.delete(categorie)
    db.commit()
    print("Catégorie supprimée :", categorie_id)
    return None
