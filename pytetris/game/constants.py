"""게임 전역 상수. PRD(docs/PRD.md) §2, 부록의 수치를 그대로 반영한다."""

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BUFFER_ROWS = 2
TOTAL_ROWS = BOARD_HEIGHT + BUFFER_ROWS

LOCK_DELAY_SECONDS = 0.5
MAX_LOCK_RESETS = 15

DAS_SECONDS = 0.3
ARR_SECONDS = 0.05

SOFT_DROP_MULTIPLIER = 20
HARD_DROP_SCORE_PER_CELL = 2
SOFT_DROP_SCORE_PER_CELL = 1

LINES_PER_LEVEL = 10
LEVEL_CAP = 20
MIN_START_LEVEL = 1
MAX_START_LEVEL = 15

NEXT_QUEUE_SIZE = 1  # MVP: 다음 블록 1개만 미리보기 (2차 개발에서 5개로 확장)

RANKING_TOP_N = 10
RANKING_NAME_MAX_LEN = 8

# 레벨별 낙하 간격(초/칸). PRD §2.1 예시(레벨1=1.0, 5=0.5, 10=0.2, 15=0.1, 20+=0.05)를
# 기준점으로 구간 선형보간한 룩업 테이블.
_ANCHORS = {1: 1.0, 5: 0.5, 10: 0.2, 15: 0.1, 20: 0.05}


def _build_fall_speed_table() -> dict[int, float]:
    table: dict[int, float] = {}
    anchor_levels = sorted(_ANCHORS)
    for level in range(1, LEVEL_CAP + 1):
        if level in _ANCHORS:
            table[level] = _ANCHORS[level]
            continue
        lower = max(a for a in anchor_levels if a < level)
        upper = min(a for a in anchor_levels if a > level)
        ratio = (level - lower) / (upper - lower)
        table[level] = round(_ANCHORS[lower] + (_ANCHORS[upper] - _ANCHORS[lower]) * ratio, 4)
    return table


FALL_SPEED_TABLE = _build_fall_speed_table()


def fall_speed_seconds(level: int) -> float:
    """레벨에 해당하는 낙하 간격(초/칸)을 반환한다. 레벨 상한(20) 이상은 최저 간격으로 고정."""
    clamped = min(max(level, MIN_START_LEVEL), LEVEL_CAP)
    return FALL_SPEED_TABLE[clamped]
