import pygame
from core.state_manager import StateManager

WIDTH, HEIGHT = 640, 360
FPS = 60
TITLE = "Guns and Boots"

# Colour palette
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (80,  80,  80)
RED    = (200, 40,  40)


class Game:
    """Main game object. Owns the window, clock and state manager."""

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.state_manager = StateManager()

        # Lazy import to avoid circular deps – states imported here
        from states.title_state import TitleState
        self.state_manager.change(TitleState(self))

    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # seconds

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            if self.state_manager.is_empty():
                self.running = False
                break

            self.state_manager.handle_events(events)
            self.state_manager.update(dt)

            self.screen.fill(BLACK)
            self.state_manager.draw(self.screen)
            pygame.display.flip()

    # ------------------------------------------------------------------
    def quit(self):
        self.running = False
