from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

import models
import schemas
from database import engine, SessionLocal
from resilience import verifier_categorie, breaker

load_dotenv()
PORT = os.getenv("PORT", "8000")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Service Tâches", version="1.0.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def accueil():
    return {"message": "Bienvenue sur le service Tâches"}


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "service-taches",
        "message": "Service opérationnel",
        "circuit_breaker_categories": breaker.state,
    }


@app.post("/api/v1/taches", response_model=schemas.TacheResponse, status_code=status.HTTP_201_CREATED)
def creer_tache(tache: schemas.TacheCreate, db: Session = Depends(get_db)):
    categorie_verifiee = None  # None = pas de catégorie demandée / pas vérifiable

    if tache.categorie_id is not None:
        resultat = verifier_categorie(tache.categorie_id)

        if resultat is False:
            # Le service-categories a répondu clairement : cette catégorie n'existe pas
            raise HTTPException(status_code=400, detail="Catégorie invalide : elle n'existe pas")

        if resultat is True:
            categorie_verifiee = True
        else:
            # resultat is None -> service-categories indisponible
            # FALLBACK / dégradation gracieuse : on crée quand même la tâche,
            # on ne bloque pas l'utilisateur pour une panne d'un autre service.
            categorie_verifiee = False
            print(f"[fallback] service-categories indisponible : tâche créée sans vérification "
                  f"(categorie_id={tache.categorie_id})")

    nouvelle_tache = models.Tache(titre=tache.titre, categorie_id=tache.categorie_id)
    db.add(nouvelle_tache)
    db.commit()
    db.refresh(nouvelle_tache)
    print("Nouvelle tâche créée :", nouvelle_tache.titre)

    reponse = schemas.TacheResponse.model_validate(nouvelle_tache)
    reponse.categorie_verifiee = categorie_verifiee
    return reponse


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
    tache.categorie_id = tache_update.categorie_id
    db.commit()
    db.refresh(tache)
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
