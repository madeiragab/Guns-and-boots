import json
import os
import pygame
from core.state_manager import StateManager

WIDTH, HEIGHT = 640, 360
SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "save.json")
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
        self.defeated_enemies = []
        self.defeated_bosses = []
        self.unlocked_players = ["Player 1"]
        self.enemy_round = 0
        self._load_save()

        # Lazy import to avoid circular deps – states imported here
        from states.title_state import TitleState
        self.state_manager.change(TitleState(self))

    # ------------------------------------------------------------------
    def _load_save(self):
        try:
            if os.path.isfile(SAVE_PATH):
                with open(SAVE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.unlocked_players = data.get("unlocked_players", ["Player 1"])
        except Exception:
            self.unlocked_players = ["Player 1"]

    def save_game(self):
        try:
            data = {"unlocked_players": list(self.unlocked_players)}
            with open(SAVE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

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
