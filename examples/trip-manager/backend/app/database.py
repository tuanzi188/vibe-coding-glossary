"""SQLite 数据库初始化和基础读写辅助函数。"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "backend" / "data" / "trips.db"
DB_PATH = Path(os.getenv("TRIP_DB_PATH", DEFAULT_DB_PATH))
if not DB_PATH.is_absolute():
    DB_PATH = PROJECT_ROOT / DB_PATH


def get_connection() -> sqlite3.Connection:
    """创建一个带行名访问能力的 SQLite 连接。"""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    """创建表并在空库中放入少量可见的学习数据。"""

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                destination TEXT NOT NULL,
                days INTEGER NOT NULL CHECK(days BETWEEN 1 AND 30),
                budget REAL NOT NULL CHECK(budget >= 0),
                status TEXT NOT NULL CHECK(status IN ('draft', 'planned', 'done')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        count = connection.execute("SELECT COUNT(*) FROM trips").fetchone()[0]
        if count == 0:
            connection.executemany(
                """
                INSERT INTO trips (title, destination, days, budget, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    ("杭州周末行", "杭州", 3, 2400, "planned"),
                    ("苏州园林慢游", "苏州", 2, 1800, "draft"),
                    ("南京历史线", "南京", 4, 3200, "done"),
                ],
            )


def fetch_all(query: str, parameters: Iterable[Any] = ()) -> list[sqlite3.Row]:
    """执行查询并返回全部结果。"""

    with get_connection() as connection:
        return list(connection.execute(query, tuple(parameters)).fetchall())
