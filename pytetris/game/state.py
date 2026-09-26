"""게임 플레이 세션 로직과 앱 전체 상태 머신.

pygame에 의존하지 않는 순수 로직이며, `ui/` 쪽에서 이 클래스를 구동한다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from .board import Board
from .constants import (
    ARR_SECONDS,
    DAS_SECONDS,
    LOCK_DELAY_SECONDS,
    MAX_LOCK_RESETS,
    SOFT_DROP_MULTIPLIER,
)
from .level import LevelManager
from .scoring import LINE_CLEAR_NAMES, hard_drop_score, line_clear_score, soft_drop_score
from .tetromino import random_piece_type, spawn_piece


class AppState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    NAME_ENTRY = auto()
    RANKING = auto()
    SETTINGS = auto()


@dataclass
class LineClearEvent:
    lines: int
    name: str


@dataclass
class GameSession:
    start_level: int = 1
    board: Board = field(init=False)
    level_manager: LevelManager = field(init=False)
    score: int = field(init=False, default=0)
    lines_cleared_total: int = field(init=False, default=0)
    game_over: bool = field(init=False, default=False)
    paused: bool = field(init=False, default=False)
    last_clear_event: LineClearEvent | None = field(init=False, default=None)
    leveled_up: bool = field(init=False, default=False)
    play_time_seconds: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        self.board = Board()
        self.level_manager = LevelManager(level=self.start_level)
        self.next_type = random_piece_type()
        self.current = None
        self.fall_timer = 0.0
        self.lock_timer = 0.0
        self.lock_resets = 0
        self.move_dir = 0
        self.das_timer = 0.0
        self.das_charged = False
        self.soft_drop_held = False
        self._spawn_next()

    # -- 내부 헬퍼 --------------------------------------------------
    def _can_move(self, drow: int, dcol: int, rotation: int | None = None) -> bool:
        cells = self.current.cells(
            rotation=rotation, row=self.current.row + drow, col=self.current.col + dcol
        )
        return self.board.is_valid_position(cells)

    def _grounded(self) -> bool:
        return not self._can_move(1, 0)

    def _reset_lock_if_grounded(self) -> None:
        if self._grounded() and self.lock_resets < MAX_LOCK_RESETS:
            self.lock_timer = 0.0
            self.lock_resets += 1

    def _spawn_next(self) -> None:
        new_piece = spawn_piece(self.next_type)
        self.next_type = random_piece_type()
        if self.board.spawn_overflow(new_piece) or self.board.is_topped_out():
            self.game_over = True
            return
        self.current = new_piece
        self.fall_timer = 0.0
        self.lock_timer = 0.0
        self.lock_resets = 0

    def _lock_current(self) -> None:
        self.board.lock_piece(self.current)
        lines = self.board.clear_full_lines()
        if lines > 0:
            self.score += line_clear_score(lines, self.level_manager.level)
            self.lines_cleared_total += lines
            self.leveled_up = self.level_manager.add_cleared_lines(lines)
            self.last_clear_event = LineClearEvent(lines, LINE_CLEAR_NAMES.get(lines, "TETRIS"))
        else:
            self.leveled_up = False
            self.last_clear_event = None
        self._spawn_next()

    # -- 외부 API(입력 처리) -----------------------------------------
    def start_move(self, direction: int) -> None:
        self.move_dir = direction
        self.das_timer = 0.0
        self.das_charged = False
        self._try_move_horizontal(direction)

    def stop_move(self, direction: int) -> None:
        if self.move_dir == direction:
            self.move_dir = 0

    def _try_move_horizontal(self, direction: int) -> bool:
        if self._can_move(0, direction):
            self.current.col += direction
            self._reset_lock_if_grounded()
            return True
        return False

    def rotate(self, direction: int) -> bool:
        """direction: +1 시계방향, -1 반시계방향. 단순 회전(SRS 킥 미포함, MVP 범위)."""
        new_rotation = (self.current.rotation + direction) % 4
        if self._can_move(0, 0, rotation=new_rotation):
            self.current.rotation = new_rotation
            self._reset_lock_if_grounded()
            return True
        return False

    def set_soft_drop(self, held: bool) -> None:
        self.soft_drop_held = held

    def hard_drop(self) -> None:
        moved_cells = 0
        while self._can_move(1, 0):
            self.current.row += 1
            moved_cells += 1
        self.score += hard_drop_score(moved_cells)
        self._lock_current()

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def consume_clear_event(self) -> LineClearEvent | None:
        event = self.last_clear_event
        self.last_clear_event = None
        return event

    def consume_level_up(self) -> bool:
        leveled = self.leveled_up
        self.leveled_up = False
        return leveled

    # -- 갱신 ----------------------------------------------------
    def update(self, dt: float) -> None:
        if self.game_over or self.paused:
            return
        self.play_time_seconds += dt
        self._update_horizontal(dt)
        self._update_fall_and_lock(dt)

    def _update_horizontal(self, dt: float) -> None:
        if self.move_dir == 0:
            return
        if not self.das_charged:
            self.das_timer += dt
            if self.das_timer >= DAS_SECONDS:
                self.das_charged = True
                self.das_timer = 0.0
                self._try_move_horizontal(self.move_dir)
        else:
            self.das_timer += dt
            while self.das_timer >= ARR_SECONDS:
                self.das_timer -= ARR_SECONDS
                if not self._try_move_horizontal(self.move_dir):
                    break

    def _update_fall_and_lock(self, dt: float) -> None:
        if self._can_move(1, 0):
            self.lock_timer = 0.0
            interval = self.level_manager.fall_interval
            if self.soft_drop_held:
                interval = max(interval / SOFT_DROP_MULTIPLIER, 1 / 60)
            self.fall_timer += dt
            while self.fall_timer >= interval and self._can_move(1, 0):
                self.fall_timer -= interval
                self.current.row += 1
                if self.soft_drop_held:
                    self.score += soft_drop_score(1)
        else:
            self.fall_timer = 0.0
            self.lock_timer += dt
            if self.lock_timer >= LOCK_DELAY_SECONDS:
                self._lock_current()
