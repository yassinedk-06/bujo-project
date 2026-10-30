"""Exceptions personnalisées du Bullet Journal."""


class BujoError(Exception):
    """Exception de base pour la bibliothèque."""


class EmptyTitleError(BujoError):
    """Levée lorsqu'un titre d'entrée est vide."""


class EntryNotFoundError(BujoError):
    """Levée lorsqu'une entrée spécifique est introuvable."""


class InvalidStateTransitionError(BujoError):
    """Levée lors d'une transition de statut interdite sur une tâche."""
