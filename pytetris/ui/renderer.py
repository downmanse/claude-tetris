"""pygame 렌더링 저수준 함수. game/ 로직 객체를 읽기만 하고 수정하지 않는다."""

from __future__ import annotations

import pygame

from ..game.board import Board
from ..game.constants import BUFFER_ROWS
from ..game.tetromino import Tetromino
from . import layout


def draw_board(surface: pygame.Surface, board: Board, origin: tuple[int, int]) -> None:
    ox, oy = origin
    rect = pygame.Rect(ox, oy, layout.PLAYFIELD_PX_WIDTH, layout.PLAYFIELD_PX_HEIGHT)
    pygame.draw.rect(surface, layout.BOARD_BG_COLOR, rect)

    for row_index, row in enumerate(board.visible_rows()):
        for col_index, color in enumerate(row):
            cell_rect = pygame.Rect(
                ox + col_index * layout.CELL_SIZE,
                oy + row_index * layout.CELL_SIZE,
                layout.CELL_SIZE,
                layout.CELL_SIZE,
            )
            if color is not None:
                pygame.draw.rect(surface, color, cell_rect)
            pygame.draw.rect(surface, layout.GRID_LINE_COLOR, cell_rect, 1)


def draw_piece(surface: pygame.Surface, piece: Tetromino, origin: tuple[int, int]) -> None:
    ox, oy = origin
    for row, col in piece.cells():
        visible_row = row - BUFFER_ROWS
        if visible_row < 0:
            continue
        cell_rect = pygame.Rect(
            ox + col * layout.CELL_SIZE,
            oy + visible_row * layout.CELL_SIZE,
            layout.CELL_SIZE,
            layout.CELL_SIZE,
        )
        pygame.draw.rect(surface, piece.color, cell_rect)
        pygame.draw.rect(surface, layout.GRID_LINE_COLOR, cell_rect, 1)


def draw_next_preview(
    surface: pygame.Surface, font: pygame.font.Font, next_piece: Tetromino, origin: tuple[int, int]
) -> None:
    ox, oy = origin
    label = font.render("NEXT", True, layout.TEXT_COLOR)
    surface.blit(label, (ox, oy))
    box_rect = pygame.Rect(ox, oy + 28, 4 * layout.CELL_SIZE, 4 * layout.CELL_SIZE)
    pygame.draw.rect(surface, layout.PANEL_BG_COLOR, box_rect)
    min_row = min(r for r, _ in next_piece.cells(rotation=0, row=0, col=0))
    min_col = min(c for _, c in next_piece.cells(rotation=0, row=0, col=0))
    for row, col in next_piece.cells(rotation=0, row=0, col=0):
        cell_rect = pygame.Rect(
            box_rect.x + (col - min_col) * layout.CELL_SIZE,
            box_rect.y + (row - min_row) * layout.CELL_SIZE,
            layout.CELL_SIZE,
            layout.CELL_SIZE,
        )
        pygame.draw.rect(surface, next_piece.color, cell_rect)
        pygame.draw.rect(surface, layout.GRID_LINE_COLOR, cell_rect, 1)


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
