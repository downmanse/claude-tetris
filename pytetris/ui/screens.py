"""AppState별 화면 구성(메뉴/플레이/일시정지/게임오버/이름입력/랭킹)."""

from __future__ import annotations

import pygame

from ..game.constants import MAX_START_LEVEL, MIN_START_LEVEL, RANKING_NAME_MAX_LEN
from ..game.state import GameSession
from ..ranking.db import RankingEntry
from . import layout, renderer

PLAYFIELD_ORIGIN = (layout.PLAYFIELD_MARGIN, layout.PLAYFIELD_MARGIN)
SIDE_PANEL_ORIGIN = (
    layout.PLAYFIELD_MARGIN * 2 + layout.PLAYFIELD_PX_WIDTH,
    layout.PLAYFIELD_MARGIN,
)


def draw_menu(surface: pygame.Surface, font, big_font, start_level: int) -> None:
    surface.fill(layout.BG_COLOR)
    renderer.draw_centered_text(
        surface, big_font, "PY TETRIS", (layout.WINDOW_WIDTH // 2, 120)
    )
    lines = [
        "ENTER / SPACE : 시작",
        "UP / DOWN : 시작 레벨 조정",
        f"시작 레벨: {start_level} (범위 {MIN_START_LEVEL}~{MAX_START_LEVEL})",
        "R : 랭킹 보기",
        "ESC : 종료",
        "",
        "조작키: 방향키 이동 / 위,X 시계회전 / Z 반시계회전",
        "스페이스 하드드롭 / 아래 소프트드롭 / P,ESC 일시정지",
    ]
    renderer.draw_text_lines(
        surface, font, lines, (layout.WINDOW_WIDTH // 2 - 180, 220), line_spacing=32
    )


def draw_playing(
    surface: pygame.Surface,
    font,
    small_font,
    session: GameSession,
    popup_text: str,
    popup_active: bool,
) -> None:
    surface.fill(layout.BG_COLOR)
    renderer.draw_board(surface, session.board, PLAYFIELD_ORIGIN)
    renderer.draw_piece(surface, session.current, PLAYFIELD_ORIGIN)

    ox, oy = SIDE_PANEL_ORIGIN
    renderer.draw_text_lines(
        surface,
        font,
        [
            "SCORE",
            f"{session.score}",
            "",
            "LEVEL",
            f"{session.level_manager.level}",
            "",
            "LINES",
            f"{session.lines_cleared_total}",
        ],
        (ox, oy),
        line_spacing=26,
    )

    from ..game.tetromino import spawn_piece

    next_piece = spawn_piece(session.next_type)
    renderer.draw_next_preview(surface, small_font, next_piece, (ox, oy + 230))

    if popup_active and popup_text:
        renderer.draw_centered_text(
            surface,
            font,
            popup_text,
            (layout.PLAYFIELD_MARGIN + layout.PLAYFIELD_PX_WIDTH // 2, 60),
            color=layout.HIGHLIGHT_COLOR,
        )


def draw_paused_overlay(surface: pygame.Surface, big_font, font) -> None:
    overlay = pygame.Surface((layout.WINDOW_WIDTH, layout.WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    renderer.draw_centered_text(
        surface, big_font, "PAUSED", (layout.WINDOW_WIDTH // 2, layout.WINDOW_HEIGHT // 2 - 20)
    )
    renderer.draw_centered_text(
        surface,
        font,
        "P/ESC 계속하기   Q 메인 메뉴로",
        (layout.WINDOW_WIDTH // 2, layout.WINDOW_HEIGHT // 2 + 30),
    )


def draw_game_over(surface: pygame.Surface, big_font, font, final_stats: dict) -> None:
    surface.fill(layout.BG_COLOR)
    renderer.draw_centered_text(
        surface, big_font, "GAME OVER", (layout.WINDOW_WIDTH // 2, 140)
    )
    lines = [
        f"최종 점수: {final_stats['score']}",
        f"레벨: {final_stats['level']}",
        f"삭제한 줄: {final_stats['lines']}",
        f"플레이 시간: {final_stats['time']}초",
        "",
        "ENTER : 다시 시작   ESC : 메인 메뉴로",
    ]
    renderer.draw_text_lines(
        surface, font, lines, (layout.WINDOW_WIDTH // 2 - 140, 220), line_spacing=32
    )


def draw_name_entry(
    surface: pygame.Surface, big_font, font, name_buffer: str, rank_preview: int
) -> None:
    surface.fill(layout.BG_COLOR)
    renderer.draw_centered_text(
        surface, big_font, "신기록입니다!", (layout.WINDOW_WIDTH // 2, 140)
    )
    renderer.draw_centered_text(
        surface,
        font,
        f"현재 {rank_preview}위!  이름을 입력하세요 (최대 {RANKING_NAME_MAX_LEN}자)",
        (layout.WINDOW_WIDTH // 2, 200),
    )
    renderer.draw_centered_text(
        surface,
        big_font,
        name_buffer + "_",
        (layout.WINDOW_WIDTH // 2, 260),
        color=layout.HIGHLIGHT_COLOR,
    )
    renderer.draw_centered_text(
        surface,
        font,
        "ENTER : 저장 (10초간 입력 없으면 PLAYER로 자동 저장)",
        (layout.WINDOW_WIDTH // 2, 320),
    )


def draw_ranking(surface: pygame.Surface, big_font, font, entries: list[RankingEntry]) -> None:
    surface.fill(layout.BG_COLOR)
    renderer.draw_centered_text(surface, big_font, "TOP 10 랭킹", (layout.WINDOW_WIDTH // 2, 60))
    if not entries:
        renderer.draw_centered_text(
            surface,
            font,
            "아직 기록이 없습니다. 첫 기록의 주인공이 되어보세요!",
            (layout.WINDOW_WIDTH // 2, 160),
        )
    else:
        lines = [
            f"{i + 1:>2}. {e.player_name:<8}  {e.score:>7}  Lv.{e.level:<2}  {e.lines_cleared}줄"
            for i, e in enumerate(entries)
        ]
        renderer.draw_text_lines(
            surface, font, lines, (layout.WINDOW_WIDTH // 2 - 220, 120), line_spacing=32
        )
    renderer.draw_centered_text(
        surface, font, "ESC : 메인 메뉴로", (layout.WINDOW_WIDTH // 2, layout.WINDOW_HEIGHT - 40)
    )
