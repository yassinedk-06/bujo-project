"""Gestion du Monthly Log (vue mensuelle) et migration des tâches."""

from __future__ import annotations

from datetime import date
from bujo.containers.daily_log import DailyLog
from bujo.core.entry import Entry, Task, TaskStatus
from bujo.exceptions import EntryNotFoundError, InvalidStateTransitionError


class MonthlyLog:
    """Conteneur des entrées et tâches prévues pour un mois donné."""

    def __init__(self, year: int, month: int) -> None:
        """Initialise un Monthly Log pour une année et un mois donnés."""
        if not (1 <= month <= 12):
            raise ValueError("Le mois doit être compris entre 1 et 12.")

        self.year: int = year
        self.month: int = month
        self.entries: dict[str, Entry] = {}

    def add_entry(self, entry: Entry) -> Entry:
        """Ajoute une entrée au Monthly Log."""
        self.entries[entry.id] = entry
        return entry

    def add_task(self, title: str, description: str = "") -> Task:
        """Crée et ajoute une tâche directement dans le Monthly Log."""
        task_date = date(self.year, self.month, 1)
        task = Task(title=title, description=description, log_date=task_date)
        self.add_entry(task)
        return task

    def get_entry(self, entry_id: str) -> Entry:
        """Récupère une entrée par son identifiant unique."""
        if entry_id not in self.entries:
            raise EntryNotFoundError(f"Entrée introuvable : {entry_id}")
        return self.entries[entry_id]

    def migrate_task_from_daily(self, daily_log: DailyLog, task_id: str) -> Task:
        """Migre une tâche depuis un Daily Log vers ce Monthly Log.

        La tâche source passe à l'état MIGRATED ('>').
        Une nouvelle tâche identique à l'état TODO est ajoutée au Monthly Log.
        """
        source_entry = daily_log.get_entry(task_id)
        if not isinstance(source_entry, Task):
            raise EntryNotFoundError(f"L'entrée {task_id} n'est pas une tâche.")

        if source_entry.status != TaskStatus.TODO:
            msg = "Seule une tâche TODO peut être migrée."
            raise InvalidStateTransitionError(msg)

        # 1. Marquer la tâche source comme migrée (symbole '>')
        source_entry.mark_migrated()

        # 2. Créer la nouvelle tâche dans le Monthly Log
        new_task = Task(
            title=source_entry.title,
            description=source_entry.description,
            log_date=date(self.year, self.month, 1),
            signifier=source_entry.signifier,
        )
        self.add_entry(new_task)
        return new_task

    def __str__(self) -> str:
        """Représentation textuelle formatée en Rapid Logging."""
        lines = [f"=== Monthly Log : {self.year}-{self.month:02d} ==="]
        for entry in self.entries.values():
            lines.append(str(entry))
        return "\n".join(lines)
