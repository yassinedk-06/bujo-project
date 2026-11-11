"""Modèles de base pour les entrées du Bullet Journal."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import date, datetime
from enum import Enum
from typing import Any

from bujo.exceptions import EmptyTitleError, InvalidStateTransitionError


class TaskStatus(str, Enum):
    """Statuts possibles pour le cycle de vie d'une tâche."""

    TODO = "TODO"
    DONE = "DONE"
    MIGRATED = "MIGRATED"
    SCHEDULED = "SCHEDULED"
    CANCELLED = "CANCELLED"


class Signifier(str, Enum):
    """Signifiants optionnels du rapid logging."""

    NONE = ""
    PRIORITY = "*"
    INSPIRATION = "!"


class Entry(ABC):
    """Classe de base abstraite représentant une entrée du journal."""

    def __init__(
        self,
        title: str,
        description: str = "",
        log_date: date | None = None,
        signifier: Signifier = Signifier.NONE,
    ) -> None:
        """Initialise une entrée avec un identifiant unique."""
        if not title.strip():
            raise EmptyTitleError("Le titre ne peut pas être vide.")

        self.id: str = str(uuid.uuid4())
        self.title: str = title.strip()
        self.description: str = description.strip()
        self.created_at: datetime = datetime.now()
        self.log_date: date = log_date or date.today()
        self.signifier: Signifier = signifier

    @abstractmethod
    def get_symbol(self) -> str:
        """Retourne le symbole d'affichage de l'entrée."""

    def to_dict(self) -> dict[str, Any]:
        """Convertit l'entrée en dictionnaire sérialisable en JSON."""
        return {
            "type": self.__class__.__name__,
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "log_date": self.log_date.isoformat(),
            "signifier": self.signifier.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Entry:
        """Reconstruit une entrée depuis un dictionnaire."""
        entry_type = data.get("type")
        signifier = Signifier(data.get("signifier", ""))
        log_date = date.fromisoformat(data["log_date"])

        if entry_type == "Task":
            entry: Entry = Task(
                title=data["title"],
                description=data.get("description", ""),
                log_date=log_date,
                signifier=signifier,
            )
            entry.status = TaskStatus(data["status"])
        elif entry_type == "Event":
            ev_time = (
                datetime.fromisoformat(data["event_time"])
                if data.get("event_time")
                else None
            )
            entry = Event(
                title=data["title"],
                event_time=ev_time,
                description=data.get("description", ""),
                log_date=log_date,
                signifier=signifier,
            )
        elif entry_type == "Note":
            entry = Note(
                title=data["title"],
                description=data.get("description", ""),
                log_date=log_date,
                signifier=signifier,
            )
        else:
            raise ValueError(f"Type d'entrée inconnu : {entry_type}")

        entry.id = data["id"]
        entry.created_at = datetime.fromisoformat(data["created_at"])
        return entry

    def __str__(self) -> str:
        """Représentation textuelle de l'entrée pour l'affichage console."""
        prefix = f"{self.signifier.value} " if self.signifier.value else ""
        return f"{prefix}{self.get_symbol()} {self.title}"


class Task(Entry):
    """Entrée représentant une tâche (peut changer d'état)."""

    def __init__(
        self,
        title: str,
        description: str = "",
        log_date: date | None = None,
        signifier: Signifier = Signifier.NONE,
    ) -> None:
        """Initialise une tâche à l'état TODO."""
        super().__init__(title, description, log_date, signifier)
        self.status: TaskStatus = TaskStatus.TODO

    def get_symbol(self) -> str:
        """Retourne le symbole correspondant au statut actuel de la tâche."""
        symbols = {
            TaskStatus.TODO: "•",
            TaskStatus.DONE: "×",
            TaskStatus.MIGRATED: ">",
            TaskStatus.SCHEDULED: "<",
            TaskStatus.CANCELLED: "~",
        }
        return symbols[self.status]

    def complete(self) -> None:
        """Marque la tâche comme terminée."""
        if self.status == TaskStatus.CANCELLED:
            msg = "Une tâche abandonnée ne peut être terminée."
            raise InvalidStateTransitionError(msg)
        self.status = TaskStatus.DONE

    def cancel(self) -> None:
        """Abandonne la tâche."""
        self.status = TaskStatus.CANCELLED

    def mark_migrated(self) -> None:
        """Marque la tâche comme migrée."""
        if self.status != TaskStatus.TODO:
            msg = "Seule une tâche TODO peut être migrée."
            raise InvalidStateTransitionError(msg)
        self.status = TaskStatus.MIGRATED

    def mark_scheduled(self) -> None:
        """Marque la tâche comme planifiée."""
        if self.status != TaskStatus.TODO:
            msg = "Seule une tâche TODO peut être planifiée."
            raise InvalidStateTransitionError(msg)
        self.status = TaskStatus.SCHEDULED

    def to_dict(self) -> dict[str, Any]:
        """Convertit la tâche en dictionnaire incluant son statut."""
        data = super().to_dict()
        data["status"] = self.status.value
        return data


class Event(Entry):
    """Entrée représentant un événement ponctuel."""

    def __init__(
        self,
        title: str,
        event_time: datetime | None = None,
        description: str = "",
        log_date: date | None = None,
        signifier: Signifier = Signifier.NONE,
    ) -> None:
        """Initialise un événement."""
        super().__init__(title, description, log_date, signifier)
        self.event_time: datetime | None = event_time

    def get_symbol(self) -> str:
        """Symbole immuable d'un événement."""
        return "○"

    def to_dict(self) -> dict[str, Any]:
        """Convertit l'événement en dictionnaire incluant son horaire."""
        data = super().to_dict()
        data["event_time"] = (
            self.event_time.isoformat() if self.event_time else None
        )
        return data


class Note(Entry):
    """Entrée représentant une note ou une information brute."""

    def get_symbol(self) -> str:
        """Symbole immuable d'une note."""
        return "–"
