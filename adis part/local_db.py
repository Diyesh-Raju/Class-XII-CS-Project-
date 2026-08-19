"""
RunCity — Student 3: Local SQLite Database
Manages run_logs and gps_points tables locally (offline-first).
Student 4 will call sync_unsent_runs() to push data to the server.
"""

import sqlite3
import os

# Place the database next to this file
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "runcity_local.db")


def get_conn() -> sqlite3.Connection:
    """Return a connection with row_factory so rows behave like dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")   # safer for concurrent writes
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db() -> None:
    """Create tables if they don't exist. Safe to call on every app start."""
    with get_conn() as conn:
        conn.executescript("""
        -- One row per completed (or in-progress) run
        CREATE TABLE IF NOT EXISTS run_logs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,           -- local user id
            started_at      TEXT    NOT NULL,           -- ISO-8601 UTC
            ended_at        TEXT,                       -- NULL while running
            distance_km     REAL    NOT NULL DEFAULT 0,
            duration_sec    INTEGER NOT NULL DEFAULT 0,
            currency_earned INTEGER NOT NULL DEFAULT 0,
            avg_speed_kmh   REAL    NOT NULL DEFAULT 0,
            avg_pace_minkm  REAL    NOT NULL DEFAULT 0, -- minutes per km
            is_valid        INTEGER NOT NULL DEFAULT 1, -- 0 = failed speed check
            synced          INTEGER NOT NULL DEFAULT 0, -- 0 = not yet sent to server
            server_run_id   INTEGER,                    -- filled in after sync
            notes           TEXT                        -- e.g. "daily cap reached"
        );

        -- Individual GPS readings for each run
        CREATE TABLE IF NOT EXISTS gps_points (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id      INTEGER NOT NULL REFERENCES run_logs(id) ON DELETE CASCADE,
            recorded_at TEXT    NOT NULL,   -- ISO-8601 UTC
            latitude    REAL    NOT NULL,
            longitude   REAL    NOT NULL,
            altitude_m  REAL,
            accuracy_m  REAL                -- GPS accuracy in metres
        );

        -- Tracks how many km the user has run today (for daily cap enforcement)
        CREATE TABLE IF NOT EXISTS daily_km (
            user_id     INTEGER NOT NULL,
            date_utc    TEXT    NOT NULL,   -- YYYY-MM-DD
            total_km    REAL    NOT NULL DEFAULT 0,
            PRIMARY KEY (user_id, date_utc)
        );
        """)


# ---------------------------------------------------------------------------
# run_logs helpers
# ---------------------------------------------------------------------------

def insert_run(user_id: int, started_at: str) -> int:
    """Open a new run row; returns the new run_id."""
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO run_logs (user_id, started_at) VALUES (?, ?)",
            (user_id, started_at),
        )
        return cur.lastrowid


def finish_run(
    run_id: int,
    ended_at: str,
    distance_km: float,
    duration_sec: int,
    currency_earned: int,
    avg_speed_kmh: float,
    avg_pace_minkm: float,
    is_valid: int,
    notes: str = "",
) -> None:
    """Update a run row when the user stops."""
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE run_logs
            SET ended_at        = ?,
                distance_km     = ?,
                duration_sec    = ?,
                currency_earned = ?,
                avg_speed_kmh   = ?,
                avg_pace_minkm  = ?,
                is_valid        = ?,
                notes           = ?
            WHERE id = ?
            """,
            (ended_at, distance_km, duration_sec, currency_earned,
             avg_speed_kmh, avg_pace_minkm, is_valid, notes, run_id),
        )


def get_run(run_id: int) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM run_logs WHERE id = ?", (run_id,)
        ).fetchone()


def get_runs_for_user(user_id: int, limit: int = 20) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM run_logs WHERE user_id = ? ORDER BY started_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()


def get_unsent_runs(user_id: int) -> list[sqlite3.Row]:
    """All completed, valid, not-yet-synced runs — for Student 4's sync layer."""
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT * FROM run_logs
            WHERE user_id = ? AND synced = 0 AND ended_at IS NOT NULL AND is_valid = 1
            """,
            (user_id,),
        ).fetchall()


def mark_run_synced(run_id: int, server_run_id: int) -> None:
    """Called by Student 4 after a successful server sync."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE run_logs SET synced = 1, server_run_id = ? WHERE id = ?",
            (server_run_id, run_id),
        )


# ---------------------------------------------------------------------------
# gps_points helpers
# ---------------------------------------------------------------------------

def insert_gps_point(
    run_id: int,
    recorded_at: str,
    latitude: float,
    longitude: float,
    altitude_m: float | None = None,
    accuracy_m: float | None = None,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO gps_points
                (run_id, recorded_at, latitude, longitude, altitude_m, accuracy_m)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (run_id, recorded_at, latitude, longitude, altitude_m, accuracy_m),
        )


def get_gps_points(run_id: int) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM gps_points WHERE run_id = ? ORDER BY recorded_at",
            (run_id,),
        ).fetchall()


# ---------------------------------------------------------------------------
# daily_km helpers
# ---------------------------------------------------------------------------

def get_daily_km(user_id: int, date_utc: str) -> float:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT total_km FROM daily_km WHERE user_id = ? AND date_utc = ?",
            (user_id, date_utc),
        ).fetchone()
        return row["total_km"] if row else 0.0


def add_daily_km(user_id: int, date_utc: str, km: float) -> float:
    """Increment daily km; returns the new total."""
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO daily_km (user_id, date_utc, total_km)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, date_utc)
            DO UPDATE SET total_km = total_km + excluded.total_km
            """,
            (user_id, date_utc, km),
        )
        row = conn.execute(
            "SELECT total_km FROM daily_km WHERE user_id = ? AND date_utc = ?",
            (user_id, date_utc),
        ).fetchone()
        return row["total_km"]
