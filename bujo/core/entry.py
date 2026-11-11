"""Modèles de base pour les entrées du Bullet Journal."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import date, datetime
from enum import Enum

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
            raise InvalidStateTransitionError("Seule une tâche TODO peut être migrée.")
        self.status = TaskStatus.MIGRATED

    def mark_scheduled(self) -> None:
        """Marque la tâche comme planifiée."""
        if self.status != TaskStatus.TODO:
            msg = "Seule une tâche TODO peut être planifiée."
            raise InvalidStateTransitionError(msg)
        self.status = TaskStatus.SCHEDULED


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


class Note(Entry):
    """Entrée représentant une note ou une information brute."""

    def get_symbol(self) -> str:
        """Symbole immuable d'une note."""
        return "–"
