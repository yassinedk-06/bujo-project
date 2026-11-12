"""Interface minimaliste Streamlit pour le Bullet Journal."""

from __future__ import annotations

import html
import re
from datetime import date, datetime, time
from pathlib import Path

import streamlit as st

from bujo.containers.daily_log import DailyLog
from bujo.containers.monthly_log import MonthlyLog
from bujo.core.entry import Entry, Event, Note, Signifier, Task, TaskStatus
from bujo.exceptions import BujoError
from bujo.logger import logger
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
TIME_PATTERN = re.compile(r"^(\d{1,2})[:h](\d{2})$")

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
h1, h2, h3, p, input, li, th, td, label {
    font-family: 'Courier New', Courier, monospace !important;
    color: #1e1e1e !important;
}
[data-testid="stSidebar"] {
    background-color: #f3efe6 !important;
    border-right: 1px solid #dfd9cc;
}
[data-baseweb="input"], [data-baseweb="base-input"], input {
    background-color: #ffffff !important;
    color: #1e1e1e !important;
    -webkit-text-fill-color: #1e1e1e !important;
    caret-color: #1e1e1e !important;
    border-color: #b8b2a6 !important;
}
input::placeholder {
    color: #7a756c !important;
    -webkit-text-fill-color: #7a756c !important;
    opacity: 1 !important;
}
.stButton > button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stDownloadButton"] > button {
    background-color: #f3efe6 !important;
    color: #1e1e1e !important;
    border: 1px solid #8c867a !important;
    border-radius: 4px !important;
    padding: 0.2rem 0.6rem !important;
    font-weight: bold !important;
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
[data-testid="stDownloadButton"] > button:hover {
    background-color: #e2dcd0 !important;
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

    event_dt: datetime | None = None
    if entry_cls is Event and tokens:
        match = TIME_PATTERN.match(tokens[0])
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                tokens.pop(0)
                event_dt = datetime.combine(log_date, time(hour, minute))

    remainder = " ".join(tokens)
    if "//" in remainder:
        title, description = [p.strip() for p in remainder.split("//", 1)]
    else:
        title, description = remainder.strip(), ""

    if entry_cls is Event:
        return Event(
            title=title,
            event_time=event_dt,
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


def render_guide() -> None:
    """Affiche la page des Clés et le guide complet du Bullet Journal."""
    st.title("Clés & Guide // Méthode BuJo")
    st.markdown(
        "Bienvenue dans votre **Bullet Journal numérique**. Dans un carnet "
        "traditionnel, la première page s'appelle la **Page des Clés (Key)** : "
        "elle répertorie les symboles et les règles du *Rapid Logging*."
    )
    st.divider()

    st.subheader("1. La Saisie Rapide (Rapid Logging)")
    st.markdown(
        "Tapez votre entrée en **une seule ligne** en commençant par une "
        "puce, puis appuyez sur **Entrée**."
    )
    st.markdown(
        "| Type | Raccourci | Symbole | Exemple de frappe |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| **Tâche** | `.` ou `•` *(ou rien)* | `•` | `. Acheter du café` |\n"
        "| **Événement** | `o` ou `○` (+ heure) | `○` | `o 14:30 Réunion` |\n"
        "| **Note** | `-` ou `–` | `–` | `- Serveur lancé sur le port 80` |"
    )

    st.subheader("2. Les Signifiants & Descriptions")
    st.markdown(
        "Ajoutez du contexte en plaçant un signifiant **tout au début** de "
        "votre ligne, ou utilisez `//` pour glisser une note détaillée :\n"
        "- `*` **(Priorité)** : Indique une tâche importante ou urgente.\n"
        "- `!` **(Inspiration)** : Met en avant une idée clé.\n"
        "- `//` **(Détail)** : Sépare le titre de sa description.\n\n"
        "**Exemples prêts à copier-coller :**\n"
        "- `* . Corriger le bug // dans storage.py avant 18h`\n"
        "- `! - Penser à documenter le projet avec Sphinx`"
    )

    st.subheader("3. Le Cycle de Vie & la Migration")
    st.markdown(
        "Dans un Bullet Journal, **on n'efface jamais rien** (pas de corbeille). "
        "Les tâches évoluent grâce aux boutons situés à droite de la ligne :\n"
        "- **`×` (Terminer)** : La tâche est accomplie (`DONE`).\n"
        "- **`>` (Migrer)** : Reporte une tâche du **Daily Log** vers le "
        "**Monthly Log** (`MIGRATED`).\n"
        "- **`<` (Planifier)** : Marque la tâche comme planifiée pour une "
        "date future (`SCHEDULED`).\n"
        "- **`~` (Abandonner)** : La tâche n'est plus pertinente (`CANCELLED`). "
        "Elle reste barrée pour conserver la trace de votre réflexion."
    )


def render_rapid_bar(log: DailyLog | MonthlyLog) -> None:
    """Affiche la barre de saisie en une ligne et l'aide-mémoire."""
    with st.form("rapid_logging_form", clear_on_submit=True):
        col_in, col_btn = st.columns([6, 1])
        with col_in:
            raw_line = st.text_input(
                "Rapid Logging",
                placeholder=(
                    "Ex: * . Finir le rapport // avant 18h  |  "
                    "o 14:30 Réunion  |  - Une idée"
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
                logger.info("Entrée ajoutée : %s", entry.title)
                st.rerun()
            except BujoError as err:
                logger.warning("Erreur de saisie rapide : %s", err)
                st.error(str(err))

    with st.expander("📖 Aide rapide : Syntaxe & Symboles"):
        st.markdown(
            "- **Types :** `.` Tâche (`•`) | `o` Événement (`○`) | "
            "`-` Note (`–`)\n"
            "- **Options :** `*` = Priorité | `!` = Idée | "
            "`14:30` après `o` = Heure | `//` = Description\n"
            "- **Actions :** `×` Terminer | `>` Migrer | `<` Planifier | "
            "`~` Abandonner\n"
            "- *Exemple :* `* . Réviser la soutenance // slides et démo`"
        )


def format_entry_html(entry: Entry) -> str:
    """Formate une entrée en HTML sécurisé selon son type et son statut."""
    raw_str = str(entry)
    if isinstance(entry, Event) and entry.event_time:
        time_str = entry.event_time.strftime("%H:%M")
        raw_str = f"{raw_str} [{time_str}]"

    safe_text = html.escape(raw_str)
    if isinstance(entry, Task):
        if entry.status in (TaskStatus.DONE, TaskStatus.CANCELLED):
            return f"<p><del>{safe_text}</del></p>"
        if entry.status in (TaskStatus.MIGRATED, TaskStatus.SCHEDULED):
            return f"<p><em>{safe_text}</em></p>"
    return f"<p><strong>{safe_text}</strong></p>"


def render_stream(log: DailyLog | MonthlyLog, is_daily: bool) -> None:
    """Affiche le flux chronologique continu sans bouton de suppression."""
    entries = list(log.entries.values())
    if not entries:
        st.caption("Page vierge. Commencez à écrire ci-dessus...")
        return

    for entry in entries:
        is_open = isinstance(entry, Task) and entry.status == TaskStatus.TODO
        if is_open and is_daily:
            cols = st.columns([6, 1, 1, 1, 1])
        elif is_open:
            cols = st.columns([7, 1, 1, 1])
        else:
            cols = st.columns([1])

        with cols[0]:
            st.markdown(format_entry_html(entry), unsafe_allow_html=True)
            if entry.description:
                st.caption(f"↳ {entry.description}")

        if is_open and isinstance(entry, Task):
            with cols[1]:
                if st.button("×", key=f"done_{entry.id}", help="Terminer"):
                    entry.complete()
                    persist_state()
                    logger.info("Tâche terminée : %s", entry.id)
                    st.rerun()
            with cols[2]:
                if st.button(
                    "<", key=f"sched_{entry.id}", help="Planifier"
                ):
                    entry.mark_scheduled()
                    persist_state()
                    logger.info("Tâche planifiée : %s", entry.id)
                    st.rerun()
            with cols[3]:
                if st.button(
                    "~", key=f"cancel_{entry.id}", help="Abandonner"
                ):
                    entry.cancel()
                    persist_state()
                    logger.info("Tâche abandonnée : %s", entry.id)
                    st.rerun()
            if is_daily:
                with cols[4]:
                    if st.button(
                        ">", key=f"mig_{entry.id}", help="Migrer au mois"
                    ):
                        st.session_state.monthly_log.migrate_task_from_daily(
                            st.session_state.daily_log, entry.id
                        )
                        persist_state()
                        logger.info("Tâche migrée : %s", entry.id)
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
        "Page ouverte",
        ["Daily Log", "Monthly Log", "Clés & Guide (Key)"],
    )

    if view == "Clés & Guide (Key)":
        render_guide()
        return

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

    if is_daily and isinstance(current_log, DailyLog):
        st.title(f"Daily Log // {current_log.log_date.isoformat()}")
        active_count = len(current_log.get_active_tasks())
        st.caption(f"• {active_count} tâche(s) en cours aujourd'hui")
    elif isinstance(current_log, MonthlyLog):
        st.title(
            f"Monthly Log // {current_log.year}.{current_log.month:02d}"
        )

    render_rapid_bar(current_log)
    st.divider()
    render_stream(current_log, is_daily=is_daily)


if __name__ == "__main__":
    main()
