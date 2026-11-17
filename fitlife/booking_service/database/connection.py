import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "booking.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS classes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT    NOT NULL,
    trainer   TEXT    NOT NULL,
    starts_at TEXT    NOT NULL,
    capacity  INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS bookings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id   INTEGER NOT NULL REFERENCES classes(id),
    client_id  INTEGER NOT NULL,
    status     TEXT    NOT NULL DEFAULT 'active',   -- active / cancelled
    created_at TEXT    NOT NULL
);
"""


@contextmanager
def db():
    """Соединение с БД: commit при успехе, rollback при исключении."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with db() as conn:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM classes").fetchone()[0] == 0:
            base = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
            conn.executemany(
                "INSERT INTO classes (title, trainer, starts_at, capacity) VALUES (?, ?, ?, ?)",
                [
                    ("Йога", "Иванова А.", base.isoformat(timespec="minutes"), 10),
                    ("Силовая тренировка", "Петров С.", (base + timedelta(hours=2)).isoformat(timespec="minutes"), 2),
                    ("Кроссфит", "Сидоров Д.", (base + timedelta(hours=4)).isoformat(timespec="minutes"), 8),
                ],
            )


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")
