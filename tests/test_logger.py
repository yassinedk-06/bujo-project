"""Tests unitaires pour la configuration du système de logging."""

import logging
from bujo.logger import setup_logger, DEBUG_LOG_FILE, ERROR_LOG_FILE


def test_logger_setup() -> None:
    """Vérifie l'initialisation du logger et de ses handlers."""
    test_log = setup_logger("bujo_test")
    assert test_log.level == logging.DEBUG
    assert len(test_log.handlers) == 3

    # Vérification de l'écriture
    test_log.debug("Message de test debug")
    test_log.error("Message de test erreur")

    assert DEBUG_LOG_FILE.exists()
    assert ERROR_LOG_FILE.exists()
