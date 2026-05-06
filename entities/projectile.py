import os
import pygame
from core.sprite_animator import SpriteAnimator
from core.paths import get_asset_path

# Caminho padrao compartilhado do projetil
DEFAULT_BULLET_PATH = get_asset_path("sprites", "bullet")
BULLET_SIZE = (32, 32)


def _load_frames_from_folder(folder, target_size=BULLET_SIZE, colorkey=(0, 0, 0)):
    """Load PNG frames from a single folder, sorted naturally."""
    import re

    def _natural_sort_key(s):
        parts = re.split(r'(\d+)', s)
        return [int(p) if p.isdigit() else p.lower() for p in parts]

    frames = []
    if not os.path.isdir(folder):
        return frames

    files = [f for f in os.listdir(folder) if f.lower().endswith('.png')]
    files.sort(key=_natural_sort_key)

    for fname in files:
        path = os.path.join(folder, fname)
        try:
            img = pygame.image.load(path)
        except Exception:
            continue
        try:
            img = img.convert_alpha()
        except Exception:
            img = img.convert()
        if img.get_alpha() is None and colorkey is not None:
            img.set_colorkey(colorkey)

        # Redimensiona para o tamanho alvo
        if target_size:
            tw, th = target_size
            try:
                img = pygame.transform.smoothscale(img, (tw, th))
            except Exception:
                img = pygame.transform.scale(img, (tw, th))

        frames.append(img)
    return frames


def load_bullet_frames(folder=None, flip=False, target_size=BULLET_SIZE):
    """Load bullet frames from a folder. Falls back to default bullet."""
    frames = []
    if folder and os.path.isdir(folder):
        frames = _load_frames_from_folder(folder, target_size=target_size)
    if not frames:
        frames = _load_frames_from_folder(DEFAULT_BULLET_PATH, target_size=target_size)
    if not frames:
        # Reserva final: quadrado amarelo
        s = pygame.Surface(BULLET_SIZE, pygame.SRCALPHA)
        s.fill((255, 220, 50, 255))
        frames = [s]
    if flip:
        frames = [pygame.transform.flip(f, True, False) for f in frames]
    return frames


class Projectile:
    """An animated bullet that travels from start_pos to end_pos over duration seconds."""

    def __init__(self, frames, start_pos, end_pos, duration=0.4, on_hit=None):
        self.animator = SpriteAnimator({"fly": frames}, default="fly", fps=14, return_to_idle=False)
        self.animator.play("fly", loop=True, reset=True)
        self.start_x, self.start_y = start_pos
        self.end_x, self.end_y = end_pos
        self.duration = max(0.05, duration)
        self.timer = 0.0
        self.finished = False
        self.on_hit = on_hit  # retorno quando o projetil chega

    @property
    def x(self):
        t = min(1.0, self.timer / self.duration)
        return self.start_x + (self.end_x - self.start_x) * t

    @property
    def y(self):
        t = min(1.0, self.timer / self.duration)
        return self.start_y + (self.end_y - self.start_y) * t

    def update(self, dt):
        if self.finished:
            return
        self.timer += dt
        self.animator.update(dt)
        if self.timer >= self.duration:
            self.finished = True
            if self.on_hit:
                self.on_hit()

    def draw(self, screen):
        if self.finished:
            return
        img = self.animator.get_image()
        if img:
            rect = img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(img, rect)
