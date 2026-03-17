import json
import os
import pygame

from entities.character import Character
from entities.projectile import load_bullet_frames, _load_frames_from_folder
from core.sprite_animator import load_animations_from_folders, SpriteAnimator

FINAL_BOSSES_BASE = os.path.join("assets", "sprites", "Final Bosses")
TARGET_FRAME_SIZE = (160, 160)


class FinalBoss(Character):
    """Adaptive final boss that scales from the current player stats."""

    def __init__(self, folder_name, player_template):
        self.folder_name = folder_name
        self._is_boss = True
        self._is_final_boss = True

        folder_path = os.path.join(FINAL_BOSSES_BASE, folder_name)

        display_name = folder_name
        base_hp = max(int(player_template.max_hp * 1.45) + 20, player_template.max_hp + 25)
        base_atk = max(int(player_template.atk * 1.45), player_template.atk + 5)
        base_def = max(int(player_template.defense * 1.40) + 1, player_template.defense + 2)

        meta_path = os.path.join(folder_path, "meta.json")
        try:
            if os.path.isfile(meta_path):
                with open(meta_path, "r", encoding="utf-8") as fh:
                    meta = json.load(fh)
                base_hp = meta.get("hp", base_hp)
                base_atk = meta.get("atk", base_atk)
                base_def = meta.get("defense", base_def)
                if "name" in meta:
                    display_name = meta["name"]
        except Exception:
            pass

        super().__init__(name=display_name, hp=base_hp, atk=base_atk, defense=base_def)
        self.profile = self.folder_name
        self.medkits = 2

        try:
            animations = {}
            if os.path.isdir(folder_path):
                animations = load_animations_from_folders(
                    folder_path, scale=1, colorkey=(0, 0, 0), target_size=TARGET_FRAME_SIZE
                )
            if animations:
                for k, frames in animations.items():
                    for i, frame in enumerate(frames):
                        try:
                            animations[k][i] = pygame.transform.flip(frame, True, False)
                        except Exception:
                            pass
        except Exception:
            animations = {}

        if not animations:
            surface = pygame.Surface(TARGET_FRAME_SIZE, pygame.SRCALPHA)
            surface.fill((140, 20, 20, 255))
            animations = {"idle": [surface]}

        special_anim_path = os.path.join(folder_path, "special", "anim")
        special_frames = _load_frames_from_folder(special_anim_path, target_size=TARGET_FRAME_SIZE)
        if special_frames:
            special_frames = [pygame.transform.flip(frame, True, False) for frame in special_frames]
            animations["special"] = special_frames

        self.animator = SpriteAnimator(animations, default="idle", fps=12, return_to_idle=True)

        self.bullet_frames = load_bullet_frames(flip=True)

        special_bullet_path = os.path.join(folder_path, "special", "bullet")
        sp_frames = _load_frames_from_folder(special_bullet_path, target_size=None)
        if sp_frames:
            self.special_bullet_frames = [pygame.transform.flip(frame, True, False) for frame in sp_frames]
        else:
            self.special_bullet_frames = self.bullet_frames

    def play(self, action):
        action = action if action in self.animator.animations else "idle"
        loop = action == "idle"
        self.animator.play(action, loop=loop, reset=True)

    def update(self, dt):
        self.animator.update(dt)

    def draw(self, screen, base_pos):
        img = self.animator.get_image()
        from core.sprite_animator import draw as draw_sprite
        draw_sprite(screen, img, base_pos)
