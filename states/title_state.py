import os
import pygame
from states.base_state import BaseState

WHITE = (255, 255, 255)
GRAY  = (100, 100, 100)
RED   = (200, 40,  40)
BLACK = (0,   0,   0)

W, H = 640, 360
BG_PATH = os.path.join("assets", "sprites", "background.png")


class TitleState(BaseState):
    """
    Tela de TITULO.
    """

    def on_enter(self):
        self._blink_timer   = 0.0
        self._blink_visible = True

        # Load background image
        self._bg = None
        try:
            if os.path.isfile(BG_PATH):
                surf = pygame.image.load(BG_PATH)
                try:
                    surf = surf.convert_alpha()
                except Exception:
                    surf = surf.convert()
                sw, sh = surf.get_size()
                scale = max(W / sw, H / sh)
                nw, nh = int(sw * scale), int(sh * scale)
                surf = pygame.transform.smoothscale(surf, (nw, nh))
                x = (nw - W) // 2
                y = (nh - H) // 2
                self._bg = surf.subsurface((x, y, W, H)).copy()
        except Exception:
            self._bg = None

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    from states.name_state import NameInputState
                    self.game.state_manager.change(NameInputState(self.game))
                elif event.key == pygame.K_ESCAPE:
                    self.game.quit()

    def update(self, dt):
        self._blink_timer += dt
        if self._blink_timer >= 0.55:
            self._blink_timer   = 0.0
            self._blink_visible = not self._blink_visible

    def draw(self, screen):
        if self._bg:
            screen.blit(self._bg, (0, 0))
        else:
            screen.fill(BLACK)

        font_big   = pygame.font.SysFont("Courier New", 36, bold=True)
        font_small = pygame.font.SysFont("Courier New", 14)

        title = font_big.render("GUNS AND BOOTS", True, WHITE)
        screen.blit(title, (W // 2 - title.get_width() // 2, H // 3))

        sub = font_small.render("um jogo tatico retro-futurista", True, GRAY)
        screen.blit(sub, (W // 2 - sub.get_width() // 2, H // 3 + 50))

        if self._blink_visible:
            prompt = font_small.render("PRESSIONE ENTER PARA INICIAR", True, WHITE)
            screen.blit(prompt, (W // 2 - prompt.get_width() // 2, H * 2 // 3))

        esc = font_small.render("ESC  sair", True, GRAY)
        screen.blit(esc, (W // 2 - esc.get_width() // 2, H - 30))
