import os
import pygame

from states.base_state import BaseState

WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
GREEN = (50, 200, 80)
BLACK = (0, 0, 0)

W, H = 640, 360
BOSSES_BASE = os.path.join("assets", "sprites", "Bosses")


class CreditsState(BaseState):
    """Final credits screen shown after defeating all bosses."""

    def on_enter(self):
        self._blink_timer = 0.0
        self._blink_visible = True
        self._friend_names = self._load_friend_names()

    def _load_friend_names(self):
        names = []
        try:
            for name in sorted(os.listdir(BOSSES_BASE), key=lambda n: n.lower()):
                if os.path.isdir(os.path.join(BOSSES_BASE, name)):
                    names.append(name)
        except Exception:
            pass
        return names

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game.complete_game()
                    from states.title_state import TitleState
                    self.game.state_manager.change(TitleState(self.game))
                elif event.key == pygame.K_ESCAPE:
                    self.game.complete_game()
                    self.game.quit()

    def update(self, dt):
        self._blink_timer += dt
        if self._blink_timer >= 0.55:
            self._blink_timer = 0.0
            self._blink_visible = not self._blink_visible

    def draw(self, screen):
        screen.fill(BLACK)

        title_font = pygame.font.SysFont("Courier New", 32, bold=True)
        line_font = pygame.font.SysFont("Courier New", 18)
        small_font = pygame.font.SysFont("Courier New", 13)

        y = 36
        title = title_font.render("CREDITOS", True, GREEN)
        screen.blit(title, (W // 2 - title.get_width() // 2, y))

        y += 62
        made_by = line_font.render("FEITO POR GABRIEL MADEIRA", True, WHITE)
        screen.blit(made_by, (W // 2 - made_by.get_width() // 2, y))

        y += 50
        thanks = line_font.render("AGRADECIMENTOS", True, WHITE)
        screen.blit(thanks, (W // 2 - thanks.get_width() // 2, y))

        y += 34
        line_1 = line_font.render("CHATGPT", True, GRAY)
        screen.blit(line_1, (W // 2 - line_1.get_width() // 2, y))

        y += 24
        line_2 = line_font.render("PROFESSOR RICARDO", True, GRAY)
        screen.blit(line_2, (W // 2 - line_2.get_width() // 2, y))

        y += 24
        if self._friend_names:
            amigos_txt = "AMIGOS: " + ", ".join(self._friend_names)
        else:
            amigos_txt = "AMIGOS"
        line_3 = small_font.render(amigos_txt, True, GRAY)
        screen.blit(line_3, (W // 2 - line_3.get_width() // 2, y))

        if self._blink_visible:
            prompt = small_font.render("ENTER -> menu inicial     ESC -> sair", True, WHITE)
            screen.blit(prompt, (W // 2 - prompt.get_width() // 2, H - 28))
