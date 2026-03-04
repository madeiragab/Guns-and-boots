import pygame
from states.base_state import BaseState

WHITE = (255, 255, 255)
GRAY  = (100, 100, 100)
RED   = (200, 40,  40)
BLACK = (0,   0,   0)

MAX_NAME_LEN = 12


class NameInputState(BaseState):
    """
    NAME_INPUT screen.
    Player types a name, confirms with ENTER.
    ESC returns to title.
    """

    def on_enter(self):
        self._name          = ""
        self._error         = ""
        self._blink_timer   = 0.0
        self._cursor_on     = True

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    name = self._name.strip()
                    if not name:
                        self._error = "Name cannot be empty."
                        return
                    # Store name and go to hub
                    from entities.player import Player
                    from states.hub_state import HubState
                    self.game.player = Player(name.upper())
                    self.game.state_manager.change(HubState(self.game))

                elif event.key == pygame.K_ESCAPE:
                    from states.title_state import TitleState
                    self.game.state_manager.change(TitleState(self.game))

                elif event.key == pygame.K_BACKSPACE:
                    self._name  = self._name[:-1]
                    self._error = ""

                else:
                    char = event.unicode
                    if char.isalpha() or char in (" ", "-", "_"):
                        if len(self._name) < MAX_NAME_LEN:
                            self._name += char
                            self._error = ""

    def update(self, dt):
        self._blink_timer += dt
        if self._blink_timer >= 0.55:
            self._blink_timer = 0.0
            self._cursor_on   = not self._cursor_on

    def draw(self, screen):
        W, H = screen.get_size()
        font_title = pygame.font.SysFont("Courier New", 28, bold=True)
        font       = pygame.font.SysFont("Courier New", 18)

        title = font_title.render("ENTER YOUR NAME", True, WHITE)
        screen.blit(title, (W // 2 - title.get_width() // 2, H // 4))

        # Input box
        box_w, box_h = 280, 32
        box_x = W // 2 - box_w // 2
        box_y = H // 2 - box_h // 2
        pygame.draw.rect(screen, (40, 40, 40), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, WHITE,        (box_x, box_y, box_w, box_h), 1)

        cursor  = "|" if self._cursor_on else " "
        display = font.render(self._name + cursor, True, WHITE)
        screen.blit(display, (box_x + 8, box_y + 6))

        # Error
        if self._error:
            err = font.render(self._error, True, RED)
            screen.blit(err, (W // 2 - err.get_width() // 2, box_y + box_h + 10))

        # Hints
        hint = pygame.font.SysFont("Courier New", 13).render(
            "ENTER confirm     ESC back", True, GRAY
        )
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 30))
