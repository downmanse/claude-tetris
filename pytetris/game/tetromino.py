"""테트로미노 정의와 회전 상태.

MVP 범위이므로 SRS 킥 테이블 없이 단순 회전만 지원한다(CLAUDE.md 개발 원칙 참고).
회전 시도가 충돌하면 그대로 회전을 취소한다.
"""

from __future__ import annotations

from dataclasses import dataclass
import random

Cell = tuple[int, int]  # (row, col)

# 각 블록 타입의 회전 상태별 셀 좌표(4x4 바운딩 박스 기준, row/col 오프셋).
_SHAPES: dict[str, list[list[Cell]]] = {
    "I": [
        [(1, 0), (1, 1), (1, 2), (1, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 1), (1, 1), (2, 1), (3, 1)],
    ],
    "O": [
        [(0, 1), (0, 2), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (1, 2)],
    ],
    "T": [
        [(0, 1), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 1)],
        [(0, 1), (1, 0), (1, 1), (2, 1)],
    ],
    "S": [
        [(0, 1), (0, 2), (1, 0), (1, 1)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 1), (1, 2), (2, 0), (2, 1)],
        [(0, 0), (1, 0), (1, 1), (2, 1)],
    ],
    "Z": [
        [(0, 0), (0, 1), (1, 1), (1, 2)],
        [(0, 2), (1, 1), (1, 2), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(0, 1), (1, 0), (1, 1), (2, 0)],
    ],
    "J": [
        [(0, 0), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 0), (2, 1)],
    ],
    "L": [
        [(0, 2), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (1, 2), (2, 0)],
        [(0, 0), (0, 1), (1, 1), (2, 1)],
    ],
}

COLORS: dict[str, tuple[int, int, int]] = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 0, 240),
    "L": (240, 160, 0),
}

PIECE_TYPES = tuple(_SHAPES.keys())

SPAWN_ROW_OFFSET = 0  # 버퍼 영역(맨 위) 기준 스폰 위치
SPAWN_COL_OFFSET = 3


@dataclass
class Tetromino:
    piece_type: str
    rotation: int = 0
    row: int = SPAWN_ROW_OFFSET
    col: int = SPAWN_COL_OFFSET

    @property
    def color(self) -> tuple[int, int, int]:
        return COLORS[self.piece_type]

    def cells(self, rotation: int | None = None, row: int | None = None, col: int | None = None) -> list[Cell]:
        """지정한(또는 현재) 회전/위치 기준 절대 셀 좌표 목록을 반환한다."""
        rot = self.rotation if rotation is None else rotation % 4
        base_row = self.row if row is None else row
        base_col = self.col if col is None else col
        shape = _SHAPES[self.piece_type][rot]
        return [(base_row + r, base_col + c) for r, c in shape]


def random_piece_type() -> str:
    """MVP 범위: 단순 균등 랜덤(2차 개발에서 7-bag으로 대체)."""
    return random.choice(PIECE_TYPES)


def spawn_piece(piece_type: str | None = None) -> Tetromino:
    return Tetromino(piece_type=piece_type or random_piece_type())
