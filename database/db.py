import sqlite3
from pathlib import Path
from typing import Any, Optional, Union

try:
    from flask import g, has_app_context
except ImportError:
    has_app_context = lambda: False
    g = None

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "lost_and_found.db"


def _create_connection(target_path: Union[Path, str]) -> sqlite3.Connection:
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


def get_db(db_path: Optional[Union[Path, str]] = None) -> sqlite3.Connection:
    """
    Get a database connection.
    If running within a Flask application context and no explicit path is passed,
    caches and reuses the connection on flask.g for the duration of the request.
    """
    if db_path is None:
        if has_app_context() and g is not None:
            if "db" not in g:
                g.db = _create_connection(DEFAULT_DB_PATH)
            return g.db
        target_path = DEFAULT_DB_PATH
    elif isinstance(db_path, str):
        target_path = Path(db_path) if db_path != ":memory:" else db_path
    else:
        target_path = db_path

    return _create_connection(target_path)


def close_db(e: Any = None) -> None:
    """
    Close the database connection safely.
    Handles both explicit Connection arguments and Flask's teardown_appcontext callback
    (which passes an exception object or None).
    """
    # 1. Close Flask request context connection if active
    if has_app_context() and g is not None:
        db = g.pop("db", None)
        if db is not None:
            try:
                db.close()
            except sqlite3.Error as exc:
                raise sqlite3.DatabaseError(
                    f"Failed to close database connection cleanly: {exc}"
                ) from exc

    # 2. If an explicit sqlite3.Connection was passed directly, close it
    if isinstance(e, sqlite3.Connection):
        try:
            e.close()
        except sqlite3.Error as exc:
            raise sqlite3.DatabaseError(
                f"Failed to close database connection cleanly: {exc}"
            ) from exc
