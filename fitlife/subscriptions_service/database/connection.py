import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "subscriptions.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tariffs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    price         REAL    NOT NULL,
    duration_days INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS subscriptions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id  INTEGER NOT NULL,
    tariff_id  INTEGER NOT NULL REFERENCES tariffs(id),
    start_date TEXT    NOT NULL,
    end_date   TEXT    NOT NULL,
    status     TEXT    NOT NULL DEFAULT 'active'
);
CREATE TABLE IF NOT EXISTS payments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id       INTEGER NOT NULL,
    tariff_id       INTEGER NOT NULL REFERENCES tariffs(id),
    subscription_id INTEGER REFERENCES subscriptions(id),
    amount          REAL    NOT NULL,
    status          TEXT    NOT NULL,          -- approved / declined
    created_at      TEXT    NOT NULL
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
        if conn.execute("SELECT COUNT(*) FROM tariffs").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO tariffs (name, price, duration_days) VALUES (?, ?, ?)",
                [("Месяц", 2500, 30), ("Квартал", 6500, 90), ("Год", 21000, 365)],
            )


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")
