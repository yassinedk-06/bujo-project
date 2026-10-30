"""Tests unitaires pour les modèles d'entrées du Bullet Journal."""

import pytest

from bujo.core import Event, Note, Signifier, Task, TaskStatus
from bujo.exceptions import EmptyTitleError, InvalidStateTransitionError


def test_task_creation_and_defaults() -> None:
    """Vérifie la création par défaut d'une tâche."""
    task = Task("Acheter du pain")
    assert task.status == TaskStatus.TODO
    assert task.get_symbol() == "•"
    assert str(task) == "• Acheter du pain"
    assert task.id is not None


def test_task_complete() -> None:
    """Vérifie le passage d'une tâche à l'état terminé."""
    task = Task("Faire le projet Python")
    task.complete()
    assert task.status == TaskStatus.DONE
    assert task.get_symbol() == "×"


def test_task_cancel_and_invalid_transition() -> None:
    """Vérifie l'abandon et l'interdiction de terminer une tâche abandonnée."""
    task = Task("Tâche inutile")
    task.cancel()
    assert task.status == TaskStatus.CANCELLED

    with pytest.raises(InvalidStateTransitionError):
        task.complete()


def test_empty_title_raises_error() -> None:
    """Vérifie qu'un titre vide lève une exception."""
    with pytest.raises(EmptyTitleError):
        Task("   ")


def test_event_and_note_display() -> None:
    """Vérifie l'affichage correct des événements et notes avec signifiants."""
    event = Event("Réunion projet", signifier=Signifier.PRIORITY)
    note = Note("Penser à utiliser uuid", signifier=Signifier.INSPIRATION)

    assert str(event) == "* ○ Réunion projet"
    assert str(note) == "! – Penser à utiliser uuid"


def test_task_migration_and_scheduling() -> None:
    """Vérifie les transitions d'état migrée et planifiée."""
    task_migrated = Task("Tâche à reporter")
    task_migrated.mark_migrated()
    assert task_migrated.status == TaskStatus.MIGRATED
    assert task_migrated.get_symbol() == ">"

    task_scheduled = Task("Tâche future")
    task_scheduled.mark_scheduled()
    assert task_scheduled.status == TaskStatus.SCHEDULED
    assert task_scheduled.get_symbol() == "<"
