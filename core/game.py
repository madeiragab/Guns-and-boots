import json
import os
import random
import pygame
from core.state_manager import StateManager

WIDTH, HEIGHT = 640, 360
SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "save.json")
ASSETS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
SFX_PATH = os.path.join(ASSETS_PATH, "sfx")
FPS = 60
TITLE = "Guns and Boots"
DEFAULT_STARTER_PLAYER = "Pablo"

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

        self._audio_ready = False
        self._current_music_path = None
        self._battle_tracks = []
        self._theme_track = None
        self._bullet_sfx = None
        self._special_sfx = None
        self._init_audio()

        self.state_manager = StateManager()
        self.defeated_enemies = []
        self.defeated_bosses = []
        self.defeated_final_bosses = []
        self.unlocked_players = [DEFAULT_STARTER_PLAYER]
        self.enemy_round = 0
        self.player_name = ""
        self.completed = False
        self._load_save()

        # Lazy import to avoid circular deps – states imported here
        from states.title_state import TitleState
        self.state_manager.change(TitleState(self))

    def _init_audio(self):
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()

            self._theme_track = os.path.join(SFX_PATH, "theme.mp3")
            self._battle_tracks = [
                os.path.join(SFX_PATH, "battle music1.mp3"),
                os.path.join(SFX_PATH, "battle music2.mp3"),
            ]

            bullet_path = os.path.join(SFX_PATH, "bullet.mp3")
            if os.path.isfile(bullet_path):
                self._bullet_sfx = pygame.mixer.Sound(bullet_path)

            special_path = os.path.join(SFX_PATH, "special.mp3")
            if os.path.isfile(special_path):
                self._special_sfx = pygame.mixer.Sound(special_path)

            self._audio_ready = True
        except Exception:
            self._audio_ready = False

    def _play_music(self, path):
        if not self._audio_ready or not path or not os.path.isfile(path):
            return
        if self._current_music_path == path:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
            self._current_music_path = path
        except Exception:
            pass

    def on_state_changed(self, state):
        """Choose soundtrack by state: theme for menu/credits, random for battles."""
        state_name = state.__class__.__name__.lower()
        if "battle" in state_name and self._battle_tracks:
            self._play_music(random.choice(self._battle_tracks))
            return
        if "title" in state_name or "credit" in state_name:
            self._play_music(self._theme_track)

    def play_bullet_sfx(self):
        if not self._audio_ready or self._bullet_sfx is None:
            return
        try:
            self._bullet_sfx.play()
        except Exception:
            pass

    def play_special_sfx(self):
        if not self._audio_ready or self._special_sfx is None:
            return
        try:
            self._special_sfx.play()
        except Exception:
            pass

    # ------------------------------------------------------------------
    def _normalize_unlocked_players(self, players):
        normalized = [name for name in players if name != "Player 1"]
        if DEFAULT_STARTER_PLAYER in normalized:
            normalized = [name for name in normalized if name != DEFAULT_STARTER_PLAYER]
        normalized.insert(0, DEFAULT_STARTER_PLAYER)

        # Keep order while removing duplicates.
        seen = set()
        unique = []
        for name in normalized:
            if name not in seen:
                seen.add(name)
                unique.append(name)
        return unique

    def _load_save(self):
        try:
            if os.path.isfile(SAVE_PATH):
                with open(SAVE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.unlocked_players = self._normalize_unlocked_players(
                    data.get("unlocked_players", [DEFAULT_STARTER_PLAYER])
                )
                self.defeated_bosses = data.get("defeated_bosses", [])
                self.defeated_final_bosses = data.get("defeated_final_bosses", [])
                self.defeated_enemies = data.get("defeated_enemies", [])
                self.enemy_round = data.get("enemy_round", 0)
                self.player_name = data.get("player_name", "")
                self.completed = data.get("completed", False)
        except Exception:
            self.unlocked_players = [DEFAULT_STARTER_PLAYER]
            self.defeated_bosses = []
            self.defeated_final_bosses = []

    def save_game(self):
        try:
            data = {
                "unlocked_players": list(self.unlocked_players),
                "defeated_bosses": list(self.defeated_bosses),
                "defeated_final_bosses": list(self.defeated_final_bosses),
                "defeated_enemies": list(self.defeated_enemies),
                "enemy_round": self.enemy_round,
                "player_name": self.player_name,
                "completed": self.completed,
            }
            with open(SAVE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def has_save(self):
        return os.path.isfile(SAVE_PATH)

    def clear_save(self):
        try:
            if os.path.isfile(SAVE_PATH):
                os.remove(SAVE_PATH)
        except Exception:
            pass
        self.unlocked_players = [DEFAULT_STARTER_PLAYER]
        self.defeated_bosses = []
        self.defeated_final_bosses = []
        self.defeated_enemies = []
        self.enemy_round = 0
        self.player_name = ""
        self.completed = False

    def complete_game(self):
        """Mark save as completed and unlock all characters."""
        self.completed = True
        players_base = os.path.join(ASSETS_PATH, "sprites", "Players")
        try:
            for name in os.listdir(players_base):
                if os.path.isdir(os.path.join(players_base, name)) and name not in self.unlocked_players:
                    self.unlocked_players.append(name)
        except Exception:
            pass
        self.save_game()

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
