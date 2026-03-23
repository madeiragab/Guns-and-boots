import os
import re
import pygame


def _natural_sort_key(s):
    parts = re.split(r'(\d+)', s)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def load_animations_from_folders(base_path, scale=1, colorkey=(0, 0, 0), target_size=None):
    """Load animations from subfolders of base_path.

    Each subfolder is treated as one animation. All .png files inside are
    loaded, naturally sorted and returned as lists of Surfaces.

    Args:
        base_path (str): path containing animation subfolders
        scale (int|float): uniform scale factor applied to each frame
        colorkey (tuple|None): color to treat as transparent if image lacks alpha
        target_size (tuple|None): desired size for the frames

    Returns:
        dict: {anim_name: [Surface, ...], ...}
    """
    animations = {}
    if not os.path.isdir(base_path):
        return animations

    for name in sorted(os.listdir(base_path), key=str.lower):
        folder = os.path.join(base_path, name)
        if not os.path.isdir(folder):
            continue

        files = [f for f in os.listdir(folder) if f.lower().endswith('.png')]
        files.sort(key=_natural_sort_key)

        frames = []
        for fname in files:
            path = os.path.join(folder, fname)
            try:
                img = pygame.image.load(path)
            except Exception:
                continue

            # preferir alfa real
            try:
                img = img.convert_alpha()
            except Exception:
                img = img.convert()

            if img.get_alpha() is None and colorkey is not None:
                img.set_colorkey(colorkey)

            # Se target_size for fornecido, redimensiona o quadro para caber enquanto
            # preserva a proporcao e posiciona em uma superficie transparente
            # do tamanho alvo ancorada na base (para alinhar os pes).
            if target_size is not None:
                tw, th = target_size
                w, h = img.get_size()
                # calcula a escala preservando a proporcao
                sx = tw / w
                sy = th / h
                s = min(sx, sy)
                new_w = max(1, int(w * s))
                new_h = max(1, int(h * s))
                try:
                    scaled = pygame.transform.smoothscale(img, (new_w, new_h))
                except Exception:
                    scaled = pygame.transform.scale(img, (new_w, new_h))

                surface = pygame.Surface((tw, th), pygame.SRCALPHA)
                # posiciona a imagem escalada para alinhar a base com a base da superficie
                dst_x = (tw - new_w) // 2
                dst_y = th - new_h
                surface.blit(scaled, (dst_x, dst_y))
                img = surface
            else:
                if scale and scale != 1:
                    w, h = img.get_size()
                    target = (int(w * scale), int(h * scale))
                    try:
                        img = pygame.transform.smoothscale(img, target)
                    except Exception:
                        img = pygame.transform.scale(img, target)

            frames.append(img)

        if frames:
            animations[name] = frames

    return animations


class SpriteAnimator:
    def __init__(self, animations, default="idle", fps=12, return_to_idle=True):
        """Control animations.

        animations: dict[str, list[Surface]]
        fps: frames per second (int)
        return_to_idle: if True, non-looping animations will return to default when finished
        """
        self.animations = animations
        self.default = default if default in animations else (next(iter(animations), None))
        self.fps = fps
        self.frame_ms = 1000.0 / max(1, fps)
        self.return_to_idle = return_to_idle

        self.current = self.default
        self.index = 0
        self.timer = 0.0  # ms
        self.loop = True
        self.finished = False

    def play(self, name, loop=False, reset=True):
        if name not in self.animations:
            name = self.default
        if reset or name != self.current:
            self.current = name
            self.index = 0
            self.timer = 0.0
            self.finished = False
            self.loop = loop

    def update(self, dt):
        """Update animation by dt seconds."""
        if not self.current or self.current not in self.animations:
            return

        ms = dt * 1000.0
        self.timer += ms
        frames = self.animations[self.current]
        if not frames:
            return

        while self.timer >= self.frame_ms:
            self.timer -= self.frame_ms
            self.index += 1
            if self.index >= len(frames):
                if self.loop or self.current == self.default:
                    self.index = 0
                else:
                    # animacao finalizada
                    self.index = len(frames) - 1
                    self.finished = True
                    if self.return_to_idle and self.default in self.animations:
                        self.play(self.default, loop=True, reset=True)
                    break

    def get_image(self):
        if not self.current or self.current not in self.animations:
            return None
        frames = self.animations[self.current]
        if not frames:
            return None
        return frames[self.index]

    def is_finished(self):
        return self.finished


def draw(surface, image, base_pos):
    if image is None:
        return
    rect = image.get_rect(midbottom=base_pos)
    surface.blit(image, rect)


def preview_frames(screen, frames, x, y, spacing=10):
    px = x
    for img in frames:
        screen.blit(img, (px, y))
        px += img.get_width() + spacing
