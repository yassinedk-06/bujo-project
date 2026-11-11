"""Tests unitaires pour la persistance JSON et l'export Markdown."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pytest

from bujo.containers.daily_log import DailyLog
from bujo.containers.monthly_log import MonthlyLog
from bujo.core.entry import Entry, Event, Note, TaskStatus
from bujo.storage import (
    export_to_markdown,
    load_daily_log,
    load_monthly_log,
    save_to_json,
)


def test_save_and_load_daily_log(tmp_path: Path) -> None:
    """Vérifie la sérialisation et désérialisation complète d'un DailyLog."""
    daily = DailyLog(log_date=date(2026, 11, 11))
    task = daily.add_task("Acheter du café", "Grain arabica")
    daily.complete_task(task.id)

    event = Event("Réunion projet", event_time=datetime(2026, 11, 11, 14, 30))
    note = Note("Idée d'architecture")
    daily.add_entry(event)
    daily.add_entry(note)

    json_file = tmp_path / "daily.json"
    save_to_json(daily, json_file)

    loaded = load_daily_log(json_file)
    assert loaded.log_date == date(2026, 11, 11)
    assert len(loaded.entries) == 3

    loaded_task = loaded.get_entry(task.id)
    assert loaded_task.title == "Acheter du café"
    assert getattr(loaded_task, "status") == TaskStatus.DONE

    loaded_event = loaded.get_entry(event.id)
    assert getattr(loaded_event, "event_time") == datetime(2026, 11, 11, 14, 30)


def test_save_and_load_monthly_log(tmp_path: Path) -> None:
    """Vérifie la sauvegarde et le chargement d'un MonthlyLog."""
    monthly = MonthlyLog(2026, 11)
    task = monthly.add_task("Préparer soutenance")

    json_file = tmp_path / "monthly.json"
    save_to_json(monthly, json_file)

    loaded = load_monthly_log(json_file)
    assert loaded.year == 2026
    assert loaded.month == 11
    assert task.id in loaded.entries


def test_from_dict_unknown_type() -> None:
    """Vérifie qu'un type inconnu dans le JSON lève une ValueError."""
    bad_data = {
        "type": "Inconnu",
        "id": "123",
        "title": "Test",
        "log_date": "2026-11-11",
        "created_at": "2026-11-11T10:00:00",
    }
    with pytest.raises(ValueError):
        Entry.from_dict(bad_data)


def test_export_to_markdown(tmp_path: Path) -> None:
    """Vérifie la génération des fichiers Markdown pour Daily et Monthly."""
    daily = DailyLog(log_date=date(2026, 11, 11))
    daily.add_task("Coder storage.py", "Ajouter JSON et MD")

    md_daily = tmp_path / "daily.md"
    content_daily = export_to_markdown(daily, md_daily)
    assert "# Daily Log - 2026-11-11" in content_daily
    assert "• Coder storage.py" in content_daily
    assert "*Ajouter JSON et MD*" in content_daily

    monthly = MonthlyLog(2026, 11)
    monthly.add_task("Objectif du mois")
    md_monthly = tmp_path / "monthly.md"
    content_monthly = export_to_markdown(monthly, md_monthly)
    assert "# Monthly Log - 2026-11" in content_monthly
