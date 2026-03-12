import os
import json
import pygame

from entities.character import Character
from entities.projectile import load_bullet_frames, _load_frames_from_folder
from core.sprite_animator import load_animations_from_folders, SpriteAnimator

BOSSES_BASE = os.path.join("assets", "sprites", "Bosses")
TARGET_FRAME_SIZE = (160, 160)


class Boss(Character):
    """A boss enemy loaded from assets/sprites/Bosses/<folder>/."""

    def __init__(self, folder_name):
        self.folder_name = folder_name
        self._is_boss = True
        folder_path = os.path.join(BOSSES_BASE, folder_name)

        # Default boss stats (tougher than regular enemies)
        display_name = folder_name
        hp, atk, defense = 50, 10, 4

        # Read meta.json if present
        meta_path = os.path.join(folder_path, "meta.json")
        try:
            if os.path.isfile(meta_path):
                with open(meta_path, "r", encoding="utf-8") as fh:
                    meta = json.load(fh)
                hp = meta.get("hp", hp)
                atk = meta.get("atk", atk)
                defense = meta.get("defense", defense)
                if "name" in meta:
                    display_name = meta["name"]
        except Exception:
            pass

        super().__init__(name=display_name, hp=hp, atk=atk, defense=defense)
        self.profile = self.folder_name

        # Load animations (flipped — boss appears on right side)
        try:
            animations = {}
            if os.path.isdir(folder_path):
                animations = load_animations_from_folders(
                    folder_path, scale=1, colorkey=(0, 0, 0), target_size=TARGET_FRAME_SIZE
                )
            if animations:
                for k, frames in animations.items():
                    for i, f in enumerate(frames):
                        try:
                            animations[k][i] = pygame.transform.flip(f, True, False)
                        except Exception:
                            pass
        except Exception:
            animations = {}

        if not animations:
            s = pygame.Surface(TARGET_FRAME_SIZE, pygame.SRCALPHA)
            s.fill((120, 20, 20, 255))
            animations = {"idle": [s]}

        # Load special/anim as "special" animation
        special_anim_path = os.path.join(folder_path, "special", "anim")
        special_frames = _load_frames_from_folder(special_anim_path, target_size=TARGET_FRAME_SIZE)
        if special_frames:
            special_frames = [pygame.transform.flip(f, True, False) for f in special_frames]
            animations["special"] = special_frames

        self.animator = SpriteAnimator(animations, default="idle", fps=12, return_to_idle=True)

        # Normal bullet (shared default, flipped)
        self.bullet_frames = load_bullet_frames(flip=True)

        # Special bullet at natural image size (no scaling)
        special_bullet_path = os.path.join(folder_path, "special", "bullet")
        sp_frames = _load_frames_from_folder(special_bullet_path, target_size=None)
        if sp_frames:
            self.special_bullet_frames = [pygame.transform.flip(f, True, False) for f in sp_frames]
        else:
            self.special_bullet_frames = self.bullet_frames

    def play(self, action):
        action = action if action in self.animator.animations else "idle"
        loop = (action == "idle")
        self.animator.play(action, loop=loop, reset=True)

    def update(self, dt):
        self.animator.update(dt)

    def draw(self, screen, base_pos):
        img = self.animator.get_image()
        from core.sprite_animator import draw as draw_sprite
        draw_sprite(screen, img, base_pos)
