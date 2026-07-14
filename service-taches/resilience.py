"""
Module de résilience pour les appels au service-categories.

Implémente :
- un TIMEOUT sur chaque appel réseau (on n'attend jamais indéfiniment)
- un RETRY (une nouvelle tentative en cas d'échec transitoire)
- un CIRCUIT BREAKER à 3 états (fermé / ouvert / semi-ouvert) pour éviter
  de marteler un service déjà en panne
- un FALLBACK : si le service-categories est injoignable, on dégrade
  gracieusement au lieu de faire planter la création de tâche.
"""

import time
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

CATEGORIES_SERVICE_URL = os.getenv("CATEGORIES_SERVICE_URL", "http://localhost:8001")
TIMEOUT_SECONDS = float(os.getenv("CATEGORIES_TIMEOUT", "2"))
MAX_RETRIES = int(os.getenv("CATEGORIES_MAX_RETRIES", "1"))

# Seuils du circuit breaker
FAILURE_THRESHOLD = 3       # nombre d'échecs consécutifs avant ouverture
OPEN_DURATION_SECONDS = 15  # durée pendant laquelle le circuit reste ouvert


class CircuitBreaker:
    """Circuit breaker minimal à 3 états : FERME, OUVERT, SEMI_OUVERT."""

    def __init__(self, failure_threshold: int, open_duration: int):
        self.failure_threshold = failure_threshold
        self.open_duration = open_duration
        self.failure_count = 0
        self.state = "FERME"
        self.opened_at = None

    def _passer_en_semi_ouvert_si_temps_ecoule(self):
        if self.state == "OUVERT" and self.opened_at is not None:
            if time.time() - self.opened_at >= self.open_duration:
                self.state = "SEMI_OUVERT"
                print("[circuit-breaker] OUVERT -> SEMI_OUVERT (on retente un appel)")

    def peut_appeler(self) -> bool:
        self._passer_en_semi_ouvert_si_temps_ecoule()
        return self.state != "OUVERT"

    def signaler_succes(self):
        if self.state != "FERME":
            print(f"[circuit-breaker] {self.state} -> FERME (service de nouveau OK)")
        self.state = "FERME"
        self.failure_count = 0
        self.opened_at = None

    def signaler_echec(self):
        self.failure_count += 1
        if self.state == "SEMI_OUVERT":
            self.state = "OUVERT"
            self.opened_at = time.time()
            print("[circuit-breaker] SEMI_OUVERT -> OUVERT (nouvel échec)")
        elif self.failure_count >= self.failure_threshold and self.state == "FERME":
            self.state = "OUVERT"
            self.opened_at = time.time()
            print(f"[circuit-breaker] FERME -> OUVERT ({self.failure_count} échecs consécutifs)")


# Une seule instance globale, partagée par tout le service
breaker = CircuitBreaker(FAILURE_THRESHOLD, OPEN_DURATION_SECONDS)


def verifier_categorie(categorie_id: int):
    """
    Vérifie qu'une catégorie existe en appelant le service-categories.

    Retourne :
      True   -> la catégorie existe (service répond, catégorie trouvée)
      False  -> le service répond mais la catégorie n'existe PAS (404)
      None   -> le service est indisponible / circuit ouvert -> on ne sait pas
                (c'est le cas de dégradation gracieuse / fallback)
    """
    if not breaker.peut_appeler():
        print("[circuit-breaker] Circuit OUVERT : appel court-circuité, fallback direct")
        return None

    derniere_erreur = None
    for tentative in range(1, MAX_RETRIES + 2):  # ex: 1 essai + 1 retry = 2 tentatives
        try:
            reponse = httpx.get(
                f"{CATEGORIES_SERVICE_URL}/api/v1/categories/{categorie_id}",
                timeout=TIMEOUT_SECONDS,
            )
            if reponse.status_code == 200:
                breaker.signaler_succes()
                return True
            elif reponse.status_code == 404:
                breaker.signaler_succes()  # le service a bien répondu, juste pas trouvé
                return False
            else:
                derniere_erreur = f"HTTP {reponse.status_code}"
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            derniere_erreur = str(e)
            print(f"[resilience] Tentative {tentative} échouée : {derniere_erreur}")

    # Toutes les tentatives ont échoué
    breaker.signaler_echec()
    return None
