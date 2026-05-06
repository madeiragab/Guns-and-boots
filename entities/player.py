import os
import pygame

from entities.character import Character
from entities.projectile import load_bullet_frames, _load_frames_from_folder, BULLET_SIZE
from core.sprite_animator import (
    load_animations_from_folders,
    SpriteAnimator,
    draw as draw_sprite,
)
from core.paths import get_asset_path


# Diretorio base contendo subpastas dos personagens jogaveis.
PLAYERS_BASE = get_asset_path("sprites", "Players")
BOSSES_BASE = get_asset_path("sprites", "Bosses")
# Deixa os sprites do jogador menores para renderizacao no jogo (aparece atras da UI, a esquerda)
TARGET_FRAME_SIZE = (160, 160)


class Player(Character):
    """Human-controlled character with sprite animations loaded from config."""

    def __init__(self, name="PLAYER", folder=None):
        super().__init__(name=name, hp=30, atk=7, defense=2)
        self.level = 1
        self.folder = folder  # nome da subpasta dentro de Players/
        self._in_boss_form = False
        self._base_form_stats = None
        self._load_animations_from_folders()
        self._load_bullet_and_special()

    def level_up(self):
        self.level += 1
        self.atk += 1
        self.max_hp += 10
        self.hp = self.max_hp

    def _load_animations_from_folders(self):
        # Define de qual pasta carregar
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

        # Carrega special/anim como animacao "special" se existir
        if self.folder:
            special_anim_path = os.path.join(PLAYERS_BASE, self.folder, "special", "anim")
            special_frames = _load_frames_from_folder(special_anim_path, target_size=TARGET_FRAME_SIZE)
            if special_frames:
                animations["special"] = special_frames

        # Usa 12 FPS conforme solicitado
        self.animator = SpriteAnimator(animations, default="idle", fps=12, return_to_idle=True)

    def _load_bullet_and_special(self):
        """Load normal bullet and special bullet frames."""
        # Tiro normal: padrao compartilhado
        self.bullet_frames = load_bullet_frames()

        # Tiro especial: de Players/<folder>/special/bullet/ (tamanho natural da imagem)
        self.special_bullet_frames = None
        if self.folder:
            special_bullet_path = os.path.join(PLAYERS_BASE, self.folder, "special", "bullet")
            frames = _load_frames_from_folder(special_bullet_path, target_size=None)
            if frames:
                self.special_bullet_frames = frames
        if not self.special_bullet_frames:
            self.special_bullet_frames = self.bullet_frames

    def _load_boss_form_visuals(self):
        """Swap visuals/projectiles to the matching Boss folder (left-side orientation)."""
        if not self.folder:
            return False

        boss_base = os.path.join(BOSSES_BASE, self.folder)
        if not os.path.isdir(boss_base):
            return False

        try:
            animations = load_animations_from_folders(
                boss_base, scale=1, colorkey=(0, 0, 0), target_size=TARGET_FRAME_SIZE
            )
        except Exception:
            animations = {}

        if not animations:
            return False

        special_anim_path = os.path.join(boss_base, "special", "anim")
        special_frames = _load_frames_from_folder(special_anim_path, target_size=TARGET_FRAME_SIZE)
        if special_frames:
            animations["special"] = special_frames

        self.animator = SpriteAnimator(animations, default="idle", fps=12, return_to_idle=True)

        self.bullet_frames = load_bullet_frames()
        special_bullet_path = os.path.join(boss_base, "special", "bullet")
        sp_frames = _load_frames_from_folder(special_bullet_path, target_size=None)
        self.special_bullet_frames = sp_frames if sp_frames else self.bullet_frames
        return True

    def activate_final_boss_form(self):
        """One-time transform used as a second chance during final boss battles."""
        if self._in_boss_form:
            return False

        self._base_form_stats = {
            "max_hp": self.max_hp,
            "atk": self.atk,
            "defense": self.defense,
            "medkits": self.medkits,
        }

        # Buffs agressivos para que a virada pareca significativa.
        self.max_hp = max(int(self.max_hp * 1.6) + 20, self.max_hp + 35)
        self.hp = self.max_hp
        self.atk = max(self.atk + 5, int(self.atk * 1.5))
        self.defense = max(self.defense + 2, int(self.defense * 1.4))
        self.medkits += 1
        self.heat = 0
        self.cover = False
        self.special_cooldown = 0

        self._in_boss_form = True
        self._load_boss_form_visuals()
        try:
            self.play("special")
        except Exception:
            pass
        return True

    def revert_from_boss_form(self):
        """Restore original visuals/stats after final battle ends."""
        if not self._in_boss_form:
            return

        stats = self._base_form_stats or {}
        self.max_hp = stats.get("max_hp", self.max_hp)
        self.atk = stats.get("atk", self.atk)
        self.defense = stats.get("defense", self.defense)
        self.medkits = stats.get("medkits", self.medkits)
        self.hp = min(max(0, self.hp), self.max_hp)

        self._base_form_stats = None
        self._in_boss_form = False
        self._load_animations_from_folders()
        self._load_bullet_and_special()
        try:
            self.play("idle")
        except Exception:
            pass

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
