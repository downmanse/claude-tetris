"""진입점: pygame 앱 루프와 상태 전환."""

from __future__ import annotations

import pygame

from .game.constants import MAX_START_LEVEL, MIN_START_LEVEL, RANKING_NAME_MAX_LEN
from .game.state import AppState, GameSession
from .ranking.db import RankingEntry, RankingRepository, now_iso8601
from .ui import layout, screens

FONT_NAME = "malgungothic"


class App:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("PyTetris")
        self.screen = pygame.display.set_mode((layout.WINDOW_WIDTH, layout.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT_NAME, 20)
        self.big_font = pygame.font.SysFont(FONT_NAME, 40)
        self.small_font = pygame.font.SysFont(FONT_NAME, 16)

        self.ranking_repo = RankingRepository()
        self.state = AppState.MENU
        self.session: GameSession | None = None
        self.start_level = MIN_START_LEVEL

        self.name_buffer = ""
        self.name_idle_timer = 0.0
        self.final_stats: dict | None = None
        self.rank_preview = 0

        self.popup_text = ""
        self.popup_timer = 0.0

        self.running = True

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()

    # -- 이벤트 처리 --------------------------------------------------
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.KEYUP:
                self._handle_keyup(event)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        key = event.key
        if self.state == AppState.MENU:
            self._handle_menu_key(key)
        elif self.state == AppState.PLAYING:
            self._handle_playing_key(key)
        elif self.state == AppState.PAUSED:
            self._handle_paused_key(key)
        elif self.state == AppState.GAME_OVER:
            self._handle_game_over_key(key)
        elif self.state == AppState.NAME_ENTRY:
            self._handle_name_entry_key(event)
        elif self.state == AppState.RANKING:
            self._handle_ranking_key(key)

    def _handle_keyup(self, event: pygame.event.Event) -> None:
        if self.state != AppState.PLAYING or self.session is None:
            return
        key = event.key
        if key == pygame.K_LEFT:
            self.session.stop_move(-1)
        elif key == pygame.K_RIGHT:
            self.session.stop_move(1)
        elif key == pygame.K_DOWN:
            self.session.set_soft_drop(False)

    def _handle_menu_key(self, key: int) -> None:
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            self._start_game()
        elif key == pygame.K_UP:
            self.start_level = min(self.start_level + 1, MAX_START_LEVEL)
        elif key == pygame.K_DOWN:
            self.start_level = max(self.start_level - 1, MIN_START_LEVEL)
        elif key == pygame.K_r:
            self.state = AppState.RANKING
        elif key == pygame.K_ESCAPE:
            self.running = False

    def _handle_playing_key(self, key: int) -> None:
        session = self.session
        assert session is not None
        if key == pygame.K_LEFT:
            session.start_move(-1)
        elif key == pygame.K_RIGHT:
            session.start_move(1)
        elif key == pygame.K_DOWN:
            session.set_soft_drop(True)
        elif key in (pygame.K_UP, pygame.K_x):
            session.rotate(1)
        elif key == pygame.K_z:
            session.rotate(-1)
        elif key == pygame.K_SPACE:
            session.hard_drop()
        elif key in (pygame.K_p, pygame.K_ESCAPE):
            session.toggle_pause()
            self.state = AppState.PAUSED

    def _handle_paused_key(self, key: int) -> None:
        session = self.session
        assert session is not None
        if key in (pygame.K_p, pygame.K_ESCAPE):
            session.toggle_pause()
            self.state = AppState.PLAYING
        elif key == pygame.K_q:
            self.session = None
            self.state = AppState.MENU

    def _handle_game_over_key(self, key: int) -> None:
        if key == pygame.K_RETURN:
            self._start_game()
        elif key == pygame.K_ESCAPE:
            self.state = AppState.MENU

    def _handle_name_entry_key(self, event: pygame.event.Event) -> None:
        key = event.key
        if key == pygame.K_RETURN:
            self._save_ranking_entry(self.name_buffer)
            return
        if key == pygame.K_BACKSPACE:
            self.name_buffer = self.name_buffer[:-1]
        elif event.unicode and event.unicode.isprintable():
            if len(self.name_buffer) < RANKING_NAME_MAX_LEN:
                self.name_buffer += event.unicode
        self.name_idle_timer = 0.0

    def _handle_ranking_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.state = AppState.MENU

    # -- 상태 전환 로직 ------------------------------------------------
    def _start_game(self) -> None:
        self.session = GameSession(start_level=self.start_level)
        self.state = AppState.PLAYING

    def _on_game_over(self) -> None:
        session = self.session
        assert session is not None
        self.final_stats = {
            "score": session.score,
            "level": session.level_manager.level,
            "lines": session.lines_cleared_total,
            "time": int(session.play_time_seconds),
        }
        if self.ranking_repo.qualifies_for_top(session.score):
            self.rank_preview = self.ranking_repo.rank_preview(session.score)
            self.name_buffer = ""
            self.name_idle_timer = 0.0
            self.state = AppState.NAME_ENTRY
        else:
            self.state = AppState.GAME_OVER

    def _save_ranking_entry(self, name: str) -> None:
        stats = self.final_stats
        assert stats is not None
        entry = RankingEntry(
            player_name=(name.strip() or "PLAYER")[:RANKING_NAME_MAX_LEN],
            score=stats["score"],
            level=stats["level"],
            lines_cleared=stats["lines"],
            play_time_seconds=stats["time"],
            played_at=now_iso8601(),
        )
        self.ranking_repo.add_entry(entry)
        self.state = AppState.RANKING

    # -- 갱신 ----------------------------------------------------
    def _update(self, dt: float) -> None:
        if self.state == AppState.PLAYING and self.session is not None:
            self.session.update(dt)
            clear_event = self.session.consume_clear_event()
            if clear_event is not None:
                self.popup_text = f"{clear_event.name}!"
                self.popup_timer = 0.8
            elif self.session.consume_level_up():
                self.popup_text = "LEVEL UP!"
                self.popup_timer = 0.5
            if self.popup_timer > 0:
                self.popup_timer -= dt
            if self.session.game_over:
                self._on_game_over()
        elif self.state == AppState.NAME_ENTRY:
            self.name_idle_timer += dt
            if self.name_idle_timer >= 10.0:
                self._save_ranking_entry(self.name_buffer or "PLAYER")

    # -- 렌더링 ---------------------------------------------------
    def _draw(self) -> None:
        if self.state == AppState.MENU:
            screens.draw_menu(self.screen, self.font, self.big_font, self.start_level)
        elif self.state == AppState.PLAYING and self.session is not None:
            screens.draw_playing(
                self.screen,
                self.font,
                self.small_font,
                self.session,
                self.popup_text,
                self.popup_timer > 0,
            )
        elif self.state == AppState.PAUSED and self.session is not None:
            screens.draw_playing(
                self.screen, self.font, self.small_font, self.session, "", False
            )
            screens.draw_paused_overlay(self.screen, self.big_font, self.font)
        elif self.state == AppState.GAME_OVER and self.final_stats is not None:
            screens.draw_game_over(self.screen, self.big_font, self.font, self.final_stats)
        elif self.state == AppState.NAME_ENTRY:
            screens.draw_name_entry(
                self.screen, self.big_font, self.font, self.name_buffer, self.rank_preview
            )
        elif self.state == AppState.RANKING:
            entries = self.ranking_repo.top_scores()
            screens.draw_ranking(self.screen, self.big_font, self.font, entries)


def main() -> None:
    App().run()


if __name__ == "__main__":
    main()
