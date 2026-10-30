"""Système de journalisation du Bullet Journal avec rotation des fichiers."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Dossier des logs à la racine du projet
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

DEBUG_LOG_FILE = LOG_DIR / "debug.log"
ERROR_LOG_FILE = LOG_DIR / "errors.log"


def setup_logger(name: str = "bujo") -> logging.Logger:
    """Configure et retourne un logger avec sortie console et fichiers tournants.

    - debug.log : capture tous les événements (DEBUG et plus),
      rotation à 1 Mo (3 backups).
    - errors.log : capture uniquement les erreurs (ERROR et plus),
      rotation à 1 Mo (3 backups).
    - console : affiche les messages informatifs (INFO et plus).
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Évite d'ajouter des doublons de handlers si setup_logger est rappelé
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 1. Handler fichier pour DEBUG (tout enregistrer)
    debug_handler = RotatingFileHandler(
        DEBUG_LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)

    # 2. Handler fichier pour ERROR (erreurs seules)
    error_handler = RotatingFileHandler(
        ERROR_LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # 3. Handler console (standard output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Instance par défaut utilisable directement
logger = setup_logger()
