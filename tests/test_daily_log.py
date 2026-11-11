"""Tests unitaires pour le conteneur DailyLog."""

import pytest
from bujo.containers.daily_log import DailyLog
from bujo.core.entry import TaskStatus
from bujo.exceptions import EntryNotFoundError


def test_add_and_complete_task() -> None:
    """Vérifie l'ajout et la complétion d'une tâche dans le Daily Log."""
    daily = DailyLog()
    task = daily.add_task("Acheter du café", "Grain arabica")
    assert task.id in daily.entries
    assert task.status == TaskStatus.TODO

    daily.complete_task(task.id)
    assert task.status == TaskStatus.DONE


def test_remove_task() -> None:
    """Vérifie la suppression d'une tâche."""
    daily = DailyLog()
    task = daily.add_task("Tâche éphémère")
    removed = daily.remove_entry(task.id)
    assert removed.id == task.id
    assert task.id not in daily.entries


def test_remove_missing_task_raises_error() -> None:
    """Vérifie qu'un identifiant inconnu lève une exception."""
    daily = DailyLog()
    with pytest.raises(EntryNotFoundError):
        daily.remove_entry("identifiant-inexistant")


def test_get_active_tasks() -> None:
    """Vérifie le filtrage des tâches en cours."""
    daily = DailyLog()
    t1 = daily.add_task("Tâche 1")
    t2 = daily.add_task("Tâche 2")
    daily.complete_task(t1.id)

    active = daily.get_active_tasks()
    assert len(active) == 1
    assert active[0].id == t2.id


def test_daily_log_str_and_invalid_complete() -> None:
    """Vérifie le __str__ du DailyLog et l'erreur sur complete d'un événement."""
    daily = DailyLog()
    daily.add_task("Tâche du jour")
    output = str(daily)
    assert "=== Daily Log :" in output
    assert "Tâche du jour" in output

    from bujo.core.entry import Event
    event = Event("Point synchro")
    daily.add_entry(event)
    with pytest.raises(EntryNotFoundError):
        daily.complete_task(event.id)
