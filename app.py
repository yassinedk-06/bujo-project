"""Interface minimaliste Streamlit pour le Bullet Journal."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import streamlit as st

from bujo.containers.daily_log import DailyLog
from bujo.containers.monthly_log import MonthlyLog
from bujo.core.entry import Entry, Event, Note, Signifier, Task, TaskStatus
from bujo.exceptions import BujoError
from bujo.storage import (
    export_to_markdown,
    load_daily_log,
    load_monthly_log,
    save_to_json,
)

DATA_DIR = Path("data")
DAILY_FILE = DATA_DIR / "daily.json"
MONTHLY_FILE = DATA_DIR / "monthly.json"
MD_FILE = DATA_DIR / "export.md"

PAPER_CSS = """
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp {
    background-color: #fcfaf2;
    background-image: radial-gradient(#d8d3c8 1px, transparent 1px);
    background-size: 22px 22px;
    color: #1e1e1e;
    font-family: 'Courier New', Courier, monospace;
}
h1, h2, h3, p, span, div, input {
    font-family: 'Courier New', Courier, monospace !important;
    color: #1e1e1e !important;
}
[data-testid="stSidebar"] {
    background-color: #f3efe6 !important;
    border-right: 1px solid #dfd9cc;
}
.stButton > button {
    background: transparent !important;
    border: 1px solid #b8b2a6 !important;
    border-radius: 3px !important;
    padding: 0.1rem 0.45rem !important;
    font-size: 0.85rem !important;
}
.stButton > button:hover {
    background-color: #e8e2d5 !important;
    border-color: #1e1e1e !important;
}
</style>
"""


def parse_rapid_input(raw_text: str, log_date: date) -> Entry:
    """Analyse une ligne de saisie rapide et retourne l'entrée associée."""
    tokens = raw_text.strip().split()
    signifier = Signifier.NONE

    if tokens and tokens[0] in ("*", "!"):
        sig_token = tokens.pop(0)
        signifier = (
            Signifier.PRIORITY
            if sig_token == "*"
            else Signifier.INSPIRATION
        )

    entry_cls: type[Entry] = Task
    if tokens and tokens[0] in ("•", ".", "○", "o", "–", "-"):
        type_token = tokens.pop(0)
        if type_token in ("○", "o"):
            entry_cls = Event
        elif type_token in ("–", "-"):
            entry_cls = Note

    remainder = " ".join(tokens)
    if "//" in remainder:
        title, description = [p.strip() for p in remainder.split("//", 1)]
    else:
        title, description = remainder.strip(), ""

    if entry_cls is Event:
        return Event(
            title=title,
            description=description,
            log_date=log_date,
            signifier=signifier,
        )
    if entry_cls is Note:
        return Note(
            title=title,
            description=description,
            log_date=log_date,
            signifier=signifier,
        )
    return Task(
        title=title,
        description=description,
        log_date=log_date,
        signifier=signifier,
    )


def init_session_state() -> None:
    """Initialise ou charge les journaux dans la session Streamlit."""
    today = date.today()
    if "daily_log" not in st.session_state:
        if DAILY_FILE.exists():
            st.session_state.daily_log = load_daily_log(DAILY_FILE)
        else:
            st.session_state.daily_log = DailyLog(log_date=today)

    if "monthly_log" not in st.session_state:
        if MONTHLY_FILE.exists():
            st.session_state.monthly_log = load_monthly_log(MONTHLY_FILE)
        else:
            st.session_state.monthly_log = MonthlyLog(
                today.year, today.month
            )


def persist_state() -> None:
    """Sauvegarde les journaux actuels sur le disque en JSON."""
    save_to_json(st.session_state.daily_log, DAILY_FILE)
    save_to_json(st.session_state.monthly_log, MONTHLY_FILE)


def render_rapid_bar(log: DailyLog | MonthlyLog) -> None:
    """Affiche la barre de saisie en une ligne (Rapid Logging)."""
    with st.form("rapid_logging_form", clear_on_submit=True):
        col_in, col_btn = st.columns([6, 1])
        with col_in:
            raw_line = st.text_input(
                "Rapid Logging",
                placeholder=(
                    "Ex: * . Finir le rapport // avant 18h  |  "
                    "o Réunion 14h  |  - Une idée"
                ),
                label_visibility="collapsed",
            )
        with col_btn:
            submitted = st.form_submit_button("Écrire ↵")

        if submitted:
            log_date = (
                log.log_date
                if isinstance(log, DailyLog)
                else date(log.year, log.month, 1)
            )
            try:
                entry = parse_rapid_input(raw_line, log_date)
                log.add_entry(entry)
                persist_state()
                st.rerun()
            except BujoError as err:
                st.error(str(err))


def render_stream(log: DailyLog | MonthlyLog, is_daily: bool) -> None:
    """Affiche le flux chronologique continu sans bouton de suppression."""
    entries = list(log.entries.values())
    if not entries:
        st.caption("Page vierge. Commencez à écrire ci-dessus...")
        return

    for entry in entries:
        is_open_task = (
            isinstance(entry, Task) and entry.status == TaskStatus.TODO
        )
        cols = (
            st.columns([7, 1, 1, 1])
            if (is_open_task and is_daily)
            else st.columns([8, 1, 1])
        )

        with cols[0]:
            if isinstance(entry, Task) and entry.status in (
                TaskStatus.DONE,
                TaskStatus.CANCELLED,
                TaskStatus.MIGRATED,
            ):
                st.markdown(f"~~{entry}~~")
            else:
                st.markdown(f"**{entry}**")
            if entry.description:
                st.caption(f"↳ {entry.description}")

        if is_open_task and isinstance(entry, Task):
            with cols[1]:
                if st.button("×", key=f"done_{entry.id}", help="Terminer"):
                    entry.complete()
                    persist_state()
                    st.rerun()
            with cols[2]:
                if st.button(
                    "~", key=f"cancel_{entry.id}", help="Abandonner"
                ):
                    entry.cancel()
                    persist_state()
                    st.rerun()
            if is_daily:
                with cols[3]:
                    if st.button(
                        ">", key=f"mig_{entry.id}", help="Migrer au mois"
                    ):
                        st.session_state.monthly_log.migrate_task_from_daily(
                            st.session_state.daily_log, entry.id
                        )
                        persist_state()
                        st.rerun()


def main() -> None:
    """Point d'entrée principal du carnet numérique."""
    st.set_page_config(
        page_title="Bullet Journal", page_icon="📓", layout="centered"
    )
    st.markdown(PAPER_CSS, unsafe_allow_html=True)
    init_session_state()

    st.sidebar.title("📓 Index")
    view = st.sidebar.radio(
        "Page ouverte", ["Daily Log", "Monthly Log"]
    )
    st.sidebar.divider()
    st.sidebar.markdown(
        "**Légende (Saisie rapide)**\n"
        "- `.` ou `•` : Tâche *(défaut)*\n"
        "- `o` ou `○` : Événement\n"
        "- `-` ou `–` : Note\n"
        "- `*` : Priorité | `!` : Idée\n"
        "- `//` : Ajouter un détail"
    )

    is_daily = view == "Daily Log"
    current_log = (
        st.session_state.daily_log
        if is_daily
        else st.session_state.monthly_log
    )

    st.sidebar.divider()
    md_content = export_to_markdown(current_log, MD_FILE)
    st.sidebar.download_button(
        label="Exporter la page (.md)",
        data=md_content,
        file_name=f"{'daily' if is_daily else 'monthly'}_log.md",
        mime="text/markdown",
    )

    if is_daily:
        st.title(f"Daily Log // {current_log.log_date.isoformat()}")
    else:
        st.title(
            f"Monthly Log // {current_log.year}.{current_log.month:02d}"
        )

    render_rapid_bar(current_log)
    st.divider()
    render_stream(current_log, is_daily=is_daily)


if __name__ == "__main__":
    main()
