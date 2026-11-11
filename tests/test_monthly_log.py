"""Tests unitaires pour le MonthlyLog et la migration de tâches."""

from __future__ import annotations

import pytest
from bujo.containers.daily_log import DailyLog
from bujo.containers.monthly_log import MonthlyLog
from bujo.core.entry import Event, TaskStatus
from bujo.exceptions import EntryNotFoundError, InvalidStateTransitionError


def test_monthly_log_initialization() -> None:
    """Vérifie l'initialisation valide et invalide d'un Monthly Log."""
    monthly = MonthlyLog(2026, 10)
    assert monthly.year == 2026
    assert monthly.month == 10

    with pytest.raises(ValueError):
        MonthlyLog(2026, 13)


def test_migrate_task_success() -> None:
    """Vérifie la migration d'une tâche d'un Daily vers un Monthly."""
    daily = DailyLog()
    task = daily.add_task("Finir rapport", "Détails financiers")

    monthly = MonthlyLog(2026, 11)
    new_task = monthly.migrate_task_from_daily(daily, task.id)

    assert task.status == TaskStatus.MIGRATED
    assert task.get_symbol() == ">"

    assert new_task.status == TaskStatus.TODO
    assert new_task.get_symbol() == "•"
    assert new_task.title == task.title
    assert new_task.id != task.id
    assert new_task.id in monthly.entries


def test_migrate_non_todo_task_raises_error() -> None:
    """Vérifie le rejet de la migration d'une tâche déjà complétée."""
    daily = DailyLog()
    task = daily.add_task("Tâche déjà faite")
    daily.complete_task(task.id)

    monthly = MonthlyLog(2026, 11)
    with pytest.raises(InvalidStateTransitionError):
        monthly.migrate_task_from_daily(daily, task.id)


def test_migrate_non_task_raises_error() -> None:
    """Vérifie le rejet lors d'une tentative de migration d'un événement."""
    daily = DailyLog()
    event = Event("Réunion")
    daily.add_entry(event)

    monthly = MonthlyLog(2026, 11)
    with pytest.raises(EntryNotFoundError):
        monthly.migrate_task_from_daily(daily, event.id)


def test_monthly_log_add_task_and_get_entry() -> None:
    """Vérifie l'ajout direct et la récupération d'une entrée."""
    monthly = MonthlyLog(2026, 11)
    task = monthly.add_task("Bilan mensuel", "Analyse des perfs")
    assert task.id in monthly.entries

    retrieved = monthly.get_entry(task.id)
    assert retrieved.id == task.id

    with pytest.raises(EntryNotFoundError):
        monthly.get_entry("id-inconnu")


def test_monthly_log_str_representation() -> None:
    """Vérifie l'affichage textuel du MonthlyLog."""
    monthly = MonthlyLog(2026, 11)
    monthly.add_task("Tâche test")
    output = str(monthly)
    assert "=== Monthly Log : 2026-11 ===" in output
    assert "Tâche test" in output
