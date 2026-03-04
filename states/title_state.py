import pygame
from states.base_state import BaseState

WHITE = (255, 255, 255)
GRAY  = (100, 100, 100)
RED   = (200, 40,  40)
BLACK = (0,   0,   0)


class TitleState(BaseState):
    """
    TITLE screen.
    Shows game title and waits for ENTER to proceed to name input.
    ESC quits.
    """

    def on_enter(self):
        self._blink_timer   = 0.0
        self._blink_visible = True

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
        W, H  = screen.get_size()
        font_big   = pygame.font.SysFont("Courier New", 36, bold=True)
        font_small = pygame.font.SysFont("Courier New", 14)

        # Title
        title = font_big.render("GUNS AND BOOTS", True, WHITE)
        screen.blit(title, (W // 2 - title.get_width() // 2, H // 3))

        # Subtitle
        sub = font_small.render("a retro-futuristic tactical game", True, GRAY)
        screen.blit(sub, (W // 2 - sub.get_width() // 2, H // 3 + 50))

        # Blinking prompt
        if self._blink_visible:
            prompt = font_small.render("PRESS ENTER TO START", True, WHITE)
            screen.blit(prompt, (W // 2 - prompt.get_width() // 2, H * 2 // 3))

        # ESC hint
        esc = font_small.render("ESC  quit", True, GRAY)
        screen.blit(esc, (W // 2 - esc.get_width() // 2, H - 30))
