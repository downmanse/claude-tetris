"""레벨/속도 관리(PRD §2.4)."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import LEVEL_CAP, LINES_PER_LEVEL, MAX_START_LEVEL, MIN_START_LEVEL, fall_speed_seconds


@dataclass
class LevelManager:
    level: int = MIN_START_LEVEL
    total_lines_cleared: int = 0

    def __post_init__(self) -> None:
        self.level = min(max(self.level, MIN_START_LEVEL), MAX_START_LEVEL)

    @property
    def fall_interval(self) -> float:
        return fall_speed_seconds(self.level)

    @property
    def lines_to_next_level(self) -> int:
        if self.level >= LEVEL_CAP:
            return 0
        threshold = self.level * LINES_PER_LEVEL
        return max(threshold - self.total_lines_cleared, 0)

    def add_cleared_lines(self, lines: int) -> bool:
        """줄 삭제를 반영하고, 레벨이 올랐으면 True를 반환한다."""
        self.total_lines_cleared += lines
        leveled_up = False
        while self.level < LEVEL_CAP and self.total_lines_cleared >= self.level * LINES_PER_LEVEL:
            self.level += 1
            leveled_up = True
        return leveled_up
