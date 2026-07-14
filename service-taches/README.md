# service-taches

API 12-factor pour la gestion des tâches. Appelle `service-categories`
pour vérifier l'existence d'une catégorie (communication inter-services).

## Configuration (variables d'environnement)

| Variable | Description | Exemple |
|---|---|---|
| `DATABASE_URL` | URL de connexion SQLite | `sqlite:///./taches.db` |
| `PORT` | Port d'écoute | `8000` |
| `CATEGORIES_SERVICE_URL` | Adresse du service-categories | `http://localhost:8001` |
| `CATEGORIES_TIMEOUT` | Timeout (secondes) des appels vers service-categories | `2` |
| `CATEGORIES_MAX_RETRIES` | Nombre de tentatives supplémentaires en cas d'échec | `1` |

Voir `.env.example`.

## Endpoints (`/api/v1`)

| Méthode | Route | Description |
|---|---|---|
| GET | `/` | Message d'accueil |
| GET | `/health` | État du service + état du circuit breaker |
| POST | `/api/v1/taches` | Créer une tâche (vérifie la catégorie si fournie) |
| GET | `/api/v1/taches` | Lister les tâches |
| GET | `/api/v1/taches/{id}` | Récupérer une tâche |
| PUT | `/api/v1/taches/{id}` | Modifier une tâche |
| DELETE | `/api/v1/taches/{id}` | Supprimer une tâche |

## Résilience

Voir `resilience.py` : timeout + retry + circuit breaker + fallback vers
`service-categories`. Détails dans le README à la racine du projet.

## Lancer

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```
