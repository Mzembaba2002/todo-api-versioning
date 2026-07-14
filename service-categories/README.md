# service-categories

API 12-factor pour la gestion des catégories de tâches.

## Configuration (variables d'environnement)

| Variable | Description | Exemple |
|---|---|---|
| `DATABASE_URL` | URL de connexion SQLite | `sqlite:///./categories.db` |
| `PORT` | Port d'écoute | `8001` |

Voir `.env.example`.

## Endpoints (`/api/v1`)

| Méthode | Route | Description |
|---|---|---|
| GET | `/` | Message d'accueil |
| GET | `/health` | État du service |
| POST | `/api/v1/categories` | Créer une catégorie |
| GET | `/api/v1/categories` | Lister les catégories |
| GET | `/api/v1/categories/{id}` | Récupérer une catégorie |
| DELETE | `/api/v1/categories/{id}` | Supprimer une catégorie |

## Lancer

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8001
```
