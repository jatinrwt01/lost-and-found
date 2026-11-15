import sqlite3
from pathlib import Path
from typing import Optional, Union

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "lost_and_found.db"


def get_db(db_path: Optional[Union[Path, str]] = None) -> sqlite3.Connection:
    if db_path is None:
        target_path = DEFAULT_DB_PATH
    elif isinstance(db_path, str):
        target_path = Path(db_path) if db_path != ":memory:" else db_path
    else:
        target_path = db_path

    conn: Optional[sqlite3.Connection] = None
    try:
        if isinstance(target_path, Path):
            target_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(target_path))
        else:
            conn = sqlite3.connect(target_path)

        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 5000;")

        return conn
    except sqlite3.Error as exc:
        if conn is not None:
            try:
                conn.close()
            except sqlite3.Error:
                pass
        raise sqlite3.DatabaseError(
            f"Failed to connect to database at '{target_path}': {exc}"
        ) from exc


def close_db(conn: Optional[sqlite3.Connection] = None) -> None:
    if conn is not None:
        try:
            conn.close()
        except sqlite3.Error as exc:
            raise sqlite3.DatabaseError(
                f"Failed to close database connection cleanly: {exc}"
            ) from exc
