"""pygame 렌더링 저수준 함수. game/ 로직 객체를 읽기만 하고 수정하지 않는다.

디자인 톤: 모서리가 크게 둥근 "젤리/마시멜로" 느낌의 블록, 은은한 하이라이트·그림자,
쨍한 원색 대신 파스텔 색상. 강한 테두리선은 사용하지 않는다.
"""

from __future__ import annotations

import pygame

from ..game.board import Board
from ..game.constants import BUFFER_ROWS
from ..game.tetromino import Tetromino
from . import layout


def _lighten(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(min(255, c + amount) for c in color)  # type: ignore[return-value]


def _darken(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(max(0, c - amount) for c in color)  # type: ignore[return-value]


def _make_jelly_cell_surface(size: int, color: tuple[int, int, int]) -> pygame.Surface:
    """둥근 모서리 + 은은한 하이라이트/그림자로 마시멜로 같은 입체감을 낸 셀 서피스를 만든다."""
    cell = pygame.Surface((size, size), pygame.SRCALPHA)
    rect = cell.get_rect()
    radius = layout.BLOCK_RADIUS

    # base body
    pygame.draw.rect(cell, color, rect, border_radius=radius)

    # 아주 은은한 바닥 그림자(테두리 대신 안쪽에 살짝)
    shadow_color = (*_darken(color, 26), 60)
    shadow_rect = rect.inflate(-4, -4)
    shadow_rect.move_ip(0, 2)
    pygame.draw.rect(cell, shadow_color, shadow_rect, border_radius=radius)

    # base body를 다시 덮어 그림자가 아래쪽에만 살짝 비치도록
    inner_rect = rect.inflate(-4, -6)
    pygame.draw.rect(cell, color, inner_rect, border_radius=radius - 2)

    # 부드러운 하이라이트(젤리 광택) - 좌상단에 살짝
    highlight_color = (*_lighten(color, 55), 90)
    highlight_rect = pygame.Rect(0, 0, int(size * 0.55), int(size * 0.4))
    highlight_rect.topleft = (int(size * 0.14), int(size * 0.12))
    pygame.draw.ellipse(cell, highlight_color, highlight_rect)

    return cell


_CELL_CACHE: dict[tuple[int, tuple[int, int, int]], pygame.Surface] = {}


def _get_jelly_cell(size: int, color: tuple[int, int, int]) -> pygame.Surface:
    key = (size, color)
    surf = _CELL_CACHE.get(key)
    if surf is None:
        surf = _make_jelly_cell_surface(size, color)
        _CELL_CACHE[key] = surf
    return surf


def _draw_cell(surface: pygame.Surface, x: int, y: int, color: tuple[int, int, int]) -> None:
    inner_size = layout.CELL_SIZE - layout.CELL_PADDING * 2
    jelly = _get_jelly_cell(inner_size, color)
    surface.blit(jelly, (x + layout.CELL_PADDING, y + layout.CELL_PADDING))


def draw_board(surface: pygame.Surface, board: Board, origin: tuple[int, int]) -> None:
    ox, oy = origin
    rect = pygame.Rect(ox, oy, layout.PLAYFIELD_PX_WIDTH, layout.PLAYFIELD_PX_HEIGHT)
    pygame.draw.rect(surface, layout.BOARD_BG_COLOR, rect, border_radius=layout.PANEL_RADIUS)

    for row_index, row in enumerate(board.visible_rows()):
        for col_index, color in enumerate(row):
            if color is None:
                continue
            x = ox + col_index * layout.CELL_SIZE
            y = oy + row_index * layout.CELL_SIZE
            _draw_cell(surface, x, y, color)


def draw_piece(surface: pygame.Surface, piece: Tetromino, origin: tuple[int, int]) -> None:
    ox, oy = origin
    for row, col in piece.cells():
        visible_row = row - BUFFER_ROWS
        if visible_row < 0:
            continue
        x = ox + col * layout.CELL_SIZE
        y = oy + visible_row * layout.CELL_SIZE
        _draw_cell(surface, x, y, piece.color)


def draw_next_preview(
    surface: pygame.Surface, font: pygame.font.Font, next_piece: Tetromino, origin: tuple[int, int]
) -> None:
    ox, oy = origin
    label = font.render("NEXT", True, layout.TEXT_MUTED_COLOR)
    surface.blit(label, (ox, oy))
    box_size = 4 * layout.CELL_SIZE
    box_rect = pygame.Rect(ox, oy + 28, box_size, box_size)
    pygame.draw.rect(surface, layout.PANEL_BG_COLOR, box_rect, border_radius=layout.PANEL_RADIUS)

    cells = next_piece.cells(rotation=0, row=0, col=0)
    min_row = min(r for r, _ in cells)
    min_col = min(c for _, c in cells)
    for row, col in cells:
        x = box_rect.x + (col - min_col) * layout.CELL_SIZE
        y = box_rect.y + (row - min_row) * layout.CELL_SIZE
        _draw_cell(surface, x, y, next_piece.color)


def draw_text_lines(
    surface: pygame.Surface,
    font: pygame.font.Font,
    lines: list[str],
    origin: tuple[int, int],
    line_spacing: int = 28,
    color: tuple[int, int, int] = layout.TEXT_COLOR,
) -> None:
    ox, oy = origin
    for index, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (ox, oy + index * line_spacing))


def draw_centered_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    center: tuple[int, int],
    color: tuple[int, int, int] = layout.TEXT_COLOR,
) -> None:
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=center)
    surface.blit(text_surface, rect)
