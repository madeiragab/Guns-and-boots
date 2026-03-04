import pygame
from states.base_state import BaseState

WHITE = (255, 255, 255)
GRAY  = (100, 100, 100)
GREEN = (50,  200, 80)
RED   = (200, 40,  40)


class ResultState(BaseState):
    """
    RESULT screen.
    Shows WIN or LOSE and lets the player return to the hub or quit.
    """

    def __init__(self, game, outcome):
        super().__init__(game)
        self.outcome = outcome   # "win" | "lose"

    def on_enter(self):
        self._blink_timer   = 0.0
        self._blink_visible = True

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    from states.hub_state import HubState
                    self.game.state_manager.change(HubState(self.game))
                elif event.key == pygame.K_ESCAPE:
                    self.game.quit()

    def update(self, dt):
        self._blink_timer += dt
        if self._blink_timer >= 0.55:
            self._blink_timer   = 0.0
            self._blink_visible = not self._blink_visible

    def draw(self, screen):
        W, H = screen.get_size()
        font_big   = pygame.font.SysFont("Courier New", 48, bold=True)
        font_mid   = pygame.font.SysFont("Courier New", 18)
        font_small = pygame.font.SysFont("Courier New", 13)

        if self.outcome == "win":
            color   = GREEN
            text    = "VICTORY"
            flavour = "Enemy neutralised."
        else:
            color   = RED
            text    = "DEFEATED"
            flavour = "You were eliminated."

        result = font_big.render(text, True, color)
        screen.blit(result, (W // 2 - result.get_width() // 2, H // 3 - 20))

        flav = font_mid.render(flavour, True, WHITE)
        screen.blit(flav, (W // 2 - flav.get_width() // 2, H // 3 + 60))

        if self._blink_visible:
            prompt = font_small.render("ENTER → hub     ESC → quit", True, GRAY)
            screen.blit(prompt, (W // 2 - prompt.get_width() // 2, H * 2 // 3))
