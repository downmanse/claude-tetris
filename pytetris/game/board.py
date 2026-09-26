"""플레이필드/충돌 판정. pygame에 의존하지 않는 순수 로직."""

from __future__ import annotations

from .constants import BOARD_WIDTH, BUFFER_ROWS, TOTAL_ROWS
from .tetromino import Cell, Tetromino

CellColor = tuple[int, int, int]


class Board:
    def __init__(self) -> None:
        self.width = BOARD_WIDTH
        self.height = TOTAL_ROWS
        self.grid: list[list[CellColor | None]] = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]

    def is_valid_position(self, cells: list[Cell]) -> bool:
        for row, col in cells:
            if col < 0 or col >= self.width or row >= self.height:
                return False
            if row < 0:
                continue  # 버퍼 위쪽은 항상 허용
            if self.grid[row][col] is not None:
                return False
        return True

    def lock_piece(self, piece: Tetromino) -> None:
        for row, col in piece.cells():
            if 0 <= row < self.height and 0 <= col < self.width:
                self.grid[row][col] = piece.color

    def spawn_overflow(self, piece: Tetromino) -> bool:
        """블록이 스폰 즉시 겹쳐서 배치할 수 없으면 True(게임 오버, PRD §2.6)."""
        return not self.is_valid_position(piece.cells())

    def clear_full_lines(self) -> int:
        remaining_rows = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = self.height - len(remaining_rows)
        if cleared > 0:
            new_rows = [[None] * self.width for _ in range(cleared)]
            self.grid = new_rows + remaining_rows
        return cleared

    def is_topped_out(self) -> bool:
        """숨겨진 버퍼 영역까지 블록이 쌓였는지 확인(PRD §2.6 탑 아웃)."""
        return any(cell is not None for cell in self.grid[BUFFER_ROWS - 1])

    def visible_rows(self) -> list[list[CellColor | None]]:
        return self.grid[BUFFER_ROWS:]
