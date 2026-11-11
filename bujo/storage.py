"""Gestion de la persistance JSON et de l'export Markdown."""

from __future__ import annotations

import json
from pathlib import Path

from bujo.containers.daily_log import DailyLog
from bujo.containers.monthly_log import MonthlyLog
from bujo.logger import logger


def save_to_json(log: DailyLog | MonthlyLog, filepath: str | Path) -> None:
    """Sauvegarde un DailyLog ou MonthlyLog dans un fichier JSON."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = log.to_dict()
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("Journal sauvegardé dans %s", path)


def load_daily_log(filepath: str | Path) -> DailyLog:
    """Charge et reconstruit un DailyLog depuis un fichier JSON."""
    path = Path(filepath)
    data = json.loads(path.read_text(encoding="utf-8"))
    logger.info("DailyLog chargé depuis %s", path)
    return DailyLog.from_dict(data)


def load_monthly_log(filepath: str | Path) -> MonthlyLog:
    """Charge et reconstruit un MonthlyLog depuis un fichier JSON."""
    path = Path(filepath)
    data = json.loads(path.read_text(encoding="utf-8"))
    logger.info("MonthlyLog chargé depuis %s", path)
    return MonthlyLog.from_dict(data)


def export_to_markdown(log: DailyLog | MonthlyLog, filepath: str | Path) -> str:
    """Exporte un DailyLog ou MonthlyLog dans un fichier Markdown."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(log, DailyLog):
        header = f"# Daily Log - {log.log_date.isoformat()}"
    else:
        header = f"# Monthly Log - {log.year}-{log.month:02d}"

    lines = [header, ""]
    for entry in log.entries.values():
        lines.append(f"- {entry}")
        if entry.description:
            lines.append(f"  *{entry.description}*")

    content = "\n".join(lines) + "\n"
    path.write_text(content, encoding="utf-8")
    logger.info("Export Markdown généré dans %s", path)
    return content
