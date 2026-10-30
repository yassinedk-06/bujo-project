"""Gestion du Daily Log (journal du jour)."""

from datetime import date
from bujo.core.entry import Entry, Task, TaskStatus
from bujo.exceptions import EntryNotFoundError


class DailyLog:
    """Conteneur des entrées associées à une journée spécifique."""

    def __init__(self, log_date: date | None = None) -> None:
        """Initialise un journal pour la date donnée (aujourd'hui par défaut)."""
        self.log_date: date = log_date or date.today()
        self.entries: dict[str, Entry] = {}

    def add_entry(self, entry: Entry) -> Entry:
        """Ajoute une entrée au Daily Log."""
        entry.log_date = self.log_date
        self.entries[entry.id] = entry
        return entry

    def add_task(self, title: str, description: str = "") -> Task:
        """Crée et ajoute une tâche au journal du jour."""
        task = Task(title=title, description=description, log_date=self.log_date)
        self.add_entry(task)
        return task

    def get_entry(self, entry_id: str) -> Entry:
        """Récupère une entrée par son identifiant unique."""
        if entry_id not in self.entries:
            raise EntryNotFoundError(f"Entrée introuvable : {entry_id}")
        return self.entries[entry_id]

    def remove_entry(self, entry_id: str) -> Entry:
        """Supprime une entrée du Daily Log."""
        if entry_id not in self.entries:
            raise EntryNotFoundError(f"Entrée introuvable : {entry_id}")
        return self.entries.pop(entry_id)

    def complete_task(self, entry_id: str) -> Task:
        """Marque une tâche comme terminée."""
        entry = self.get_entry(entry_id)
        if not isinstance(entry, Task):
            raise EntryNotFoundError(f"L'entrée {entry_id} n'est pas une tâche.")
        entry.complete()
        return entry

    def get_active_tasks(self) -> list[Task]:
        """Retourne la liste des tâches en cours (TODO)."""
        return [
            entry
            for entry in self.entries.values()
            if isinstance(entry, Task) and entry.status == TaskStatus.TODO
        ]

    def __str__(self) -> str:
        """Représentation textuelle du Daily Log."""
        lines = [f"=== Daily Log : {self.log_date} ==="]
        for entry in self.entries.values():
            lines.append(str(entry))
        return "\n".join(lines)
