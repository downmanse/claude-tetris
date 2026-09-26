"""점수 계산. MVP 범위: Single/Double/Triple/Tetris 기본 점수 + 드롭 보너스만 구현.

T-스핀, 콤보, 백투백, 퍼펙트클리어는 2차 개발 항목이므로 여기서 다루지 않는다(CLAUDE.md 우선순위 원칙).
"""

from __future__ import annotations

from .constants import HARD_DROP_SCORE_PER_CELL, SOFT_DROP_SCORE_PER_CELL

_LINE_CLEAR_BASE_SCORE = {
    1: 100,   # Single
    2: 300,   # Double
    3: 500,   # Triple
    4: 800,   # Tetris
}

LINE_CLEAR_NAMES = {
    1: "SINGLE",
    2: "DOUBLE",
    3: "TRIPLE",
    4: "TETRIS",
}


def line_clear_score(lines_cleared: int, level: int) -> int:
    if lines_cleared <= 0:
        return 0
    base = _LINE_CLEAR_BASE_SCORE.get(lines_cleared, _LINE_CLEAR_BASE_SCORE[4])
    return base * level


def soft_drop_score(cells: int) -> int:
    return cells * SOFT_DROP_SCORE_PER_CELL


def hard_drop_score(cells: int) -> int:
    return cells * HARD_DROP_SCORE_PER_CELL
