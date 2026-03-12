import os
import pygame

from entities.character import Character
from core.sprite_animator import (
    load_animations_from_folders,
    SpriteAnimator,
    draw as draw_sprite,
)


# The player now loads animations from folders under assets/sprites/Player/
# Each subfolder should contain PNG frames for that animation.
ANIM_BASE = os.path.join("assets", "sprites", "Player")
# Make player sprites smaller for in-game rendering (appears behind UI on left)
# Adjust these values to taste (w, h).
TARGET_FRAME_SIZE = (160, 160)


class Player(Character):
    """Human-controlled character with sprite animations loaded from config."""

    def __init__(self, name="PLAYER"):
        super().__init__(name=name, hp=30, atk=7, defense=2)
        self._load_animations_from_folders()

    def _load_animations_from_folders(self):
        # Try loading all animations from subfolders. If none found, fall back
        # to a minimal placeholder so the game won't crash.
        try:
            animations = load_animations_from_folders(ANIM_BASE, scale=1, colorkey=(0, 0, 0), target_size=TARGET_FRAME_SIZE)
        except Exception:
            animations = {}

        if not animations:
            # fallback single placeholder frame
            s = pygame.Surface(TARGET_FRAME_SIZE, pygame.SRCALPHA)
            s.fill((150, 0, 0, 255))
            animations = {"idle": [s]}

        # Use 12 FPS as requested
        self.animator = SpriteAnimator(animations, default="idle", fps=12, return_to_idle=True)

    # ------------------------------------------------------------------
    def play(self, action):
        action = action if action in self.animator.animations else "idle"
        loop = (action == "idle")
        self.animator.play(action, loop=loop, reset=True)

    def update(self, dt):
        self.animator.update(dt)

    def draw(self, screen, base_pos):
        img = self.animator.get_image()
        draw_sprite(screen, img, base_pos)
