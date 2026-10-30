"""Tests unitaires de base pour valider l'environnement."""

import bujo


def test_package_version() -> None:
    """Vérifie la version du package."""
    assert bujo.__version__ == "0.1.0"
