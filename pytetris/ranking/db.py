"""로컬 SQLite 랭킹 저장소(PRD §2.7, §4.2)."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from platformdirs import user_data_dir

from ..game.constants import RANKING_TOP_N

_APP_NAME = "PyTetris"


@dataclass
class RankingEntry:
    player_name: str
    score: int
    level: int
    lines_cleared: int
    play_time_seconds: int
    played_at: str


def default_db_path() -> Path:
    data_dir = Path(user_data_dir(_APP_NAME))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "ranking.db"


class RankingRepository:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or default_db_path()
        self._ensure_usable_db()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _ensure_usable_db(self) -> None:
        if not self.db_path.exists():
            return
        try:
            with closing(self._connect()) as conn:
                result = conn.execute("PRAGMA integrity_check").fetchone()
                if result is None or result[0] != "ok":
                    raise sqlite3.DatabaseError("integrity check failed")
        except sqlite3.DatabaseError:
            backup_path = self.db_path.with_suffix(".corrupt.bak")
            self.db_path.replace(backup_path)

    def _init_schema(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ranking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    level INTEGER NOT NULL,
                    lines_cleared INTEGER NOT NULL,
                    play_time_seconds INTEGER NOT NULL,
                    played_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def qualifies_for_top(self, score: int) -> bool:
        top = self.top_scores(RANKING_TOP_N)
        if len(top) < RANKING_TOP_N:
            return True
        return score > top[-1].score

    def rank_preview(self, score: int) -> int:
        """이 점수를 저장할 경우 예상되는 순위(1위부터)를 반환한다."""
        top = self.top_scores(RANKING_TOP_N)
        return sum(1 for e in top if e.score > score) + 1

    def add_entry(self, entry: RankingEntry) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO ranking
                    (player_name, score, level, lines_cleared, play_time_seconds, played_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.player_name,
                    entry.score,
                    entry.level,
                    entry.lines_cleared,
                    entry.play_time_seconds,
                    entry.played_at,
                ),
            )
            conn.commit()

    def top_scores(self, limit: int = RANKING_TOP_N) -> list[RankingEntry]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT player_name, score, level, lines_cleared, play_time_seconds, played_at
                FROM ranking
                ORDER BY score DESC, played_at ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [RankingEntry(*row) for row in rows]


def now_iso8601() -> str:
    return datetime.now(timezone.utc).isoformat()
