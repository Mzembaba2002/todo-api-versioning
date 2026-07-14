# TP Microservices — API ToDo découpée

Découpage de l'API monolithique ToDo (Séance 03) en 2 microservices autonomes.

## Architecture

```
service-categories (port 8001)      service-taches (port 8000)
   base: categories.db                  base: taches.db
   ------------------------             ------------------------
   POST   /api/v1/categories            POST   /api/v1/taches   ---> appelle
   GET    /api/v1/categories            GET    /api/v1/taches        service-categories
   GET    /api/v1/categories/{id}  <----GET    /api/v1/taches/{id}   en HTTP (synchrone)
   DELETE /api/v1/categories/{id}       PUT    /api/v1/taches/{id}
   GET    /health                       DELETE /api/v1/taches/{id}
                                         GET    /health
```

- **service-categories** : gère les catégories de tâches. Autonome, sa propre base SQLite.
- **service-taches** : gère les tâches (CRUD). Quand on crée une tâche avec une `categorie_id`,
  il appelle `service-categories` en HTTP pour vérifier qu'elle existe.

## Communication inter-services

`service-taches` → `service-categories` via HTTP/REST synchrone :
`GET {CATEGORIES_SERVICE_URL}/api/v1/categories/{id}`

L'adresse n'est jamais codée en dur : elle vient de la variable d'environnement
`CATEGORIES_SERVICE_URL` (voir `.env.example` de service-taches).

## Résilience

Implémentée dans `service-taches/resilience.py` :
- **Timeout** (2s par défaut) sur chaque appel réseau.
- **Retry** : une nouvelle tentative en cas d'échec transitoire.
- **Circuit breaker** à 3 états (FERME / OUVERT / SEMI_OUVERT) : après 3 échecs
  consécutifs, le circuit s'ouvre et court-circuite les appels suivants pendant 15s,
  au lieu de re-tenter (et de re-timeout) à chaque fois.
- **Fallback / dégradation gracieuse** : si `service-categories` est indisponible,
  la tâche est quand même créée, avec `"categorie_verifiee": false` dans la réponse,
  plutôt que de renvoyer une erreur 500 à l'utilisateur.

## Lancer le projet en local

Dans deux terminaux séparés :

```bash
# Terminal 1
cd service-categories
python -m venv venv && source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8001

# Terminal 2
cd service-taches
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

## Lancer avec Docker Compose (bonus)

```bash
docker compose up --build
```

## Démonstration (captures pour le rapport)

Voir la section "Captures à faire" fournie séparément.
