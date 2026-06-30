from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Récupérer l'adresse de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")

# Connexion à SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Création des sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Classe de base pour les modèles
Base = declarative_base()