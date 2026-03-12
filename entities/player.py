import os
import pygame

from entities.character import Character
from entities.projectile import load_bullet_frames, _load_frames_from_folder, BULLET_SIZE
from core.sprite_animator import (
    load_animations_from_folders,
    SpriteAnimator,
    draw as draw_sprite,
)


# Base directory containing player character sub-folders.
PLAYERS_BASE = os.path.join("assets", "sprites", "Players")
# Make player sprites smaller for in-game rendering (appears behind UI on left)
TARGET_FRAME_SIZE = (160, 160)


class Player(Character):
    """Human-controlled character with sprite animations loaded from config."""

    def __init__(self, name="PLAYER", folder=None):
        super().__init__(name=name, hp=30, atk=7, defense=2)
        self.level = 1
        self.folder = folder  # subfolder name inside Players/
        self._load_animations_from_folders()
        self._load_bullet_and_special()

    def level_up(self):
        self.level += 1
        self.atk += 1
        self.max_hp += 10
        self.hp = self.max_hp

    def _load_animations_from_folders(self):
        # Determine which folder to load from
        if self.folder:
            anim_base = os.path.join(PLAYERS_BASE, self.folder)
        else:
            anim_base = PLAYERS_BASE

        try:
            animations = load_animations_from_folders(anim_base, scale=1, colorkey=(0, 0, 0), target_size=TARGET_FRAME_SIZE)
        except Exception:
            animations = {}

        if not animations:
            s = pygame.Surface(TARGET_FRAME_SIZE, pygame.SRCALPHA)
            s.fill((150, 0, 0, 255))
            animations = {"idle": [s]}

        # Load special/anim as the "special" animation if it exists
        if self.folder:
            special_anim_path = os.path.join(PLAYERS_BASE, self.folder, "special", "anim")
            special_frames = _load_frames_from_folder(special_anim_path, target_size=TARGET_FRAME_SIZE)
            if special_frames:
                animations["special"] = special_frames

        # Use 12 FPS as requested
        self.animator = SpriteAnimator(animations, default="idle", fps=12, return_to_idle=True)

    def _load_bullet_and_special(self):
        """Load normal bullet and special bullet frames."""
        # Normal bullet: shared default
        self.bullet_frames = load_bullet_frames()

        # Special bullet: from Players/<folder>/special/bullet/ (natural image size)
        self.special_bullet_frames = None
        if self.folder:
            special_bullet_path = os.path.join(PLAYERS_BASE, self.folder, "special", "bullet")
            frames = _load_frames_from_folder(special_bullet_path, target_size=None)
            if frames:
                self.special_bullet_frames = frames
        if not self.special_bullet_frames:
            self.special_bullet_frames = self.bullet_frames

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
