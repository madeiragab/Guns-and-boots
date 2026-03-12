import pygame
import os


def load_sprite_sheet(path, frame_width, frame_height, scale=1, colorkey=(0, 0, 0)):
    """Load a sprite sheet and cut it into frames by grid.

    Args:
        path (str): path to image file
        frame_width (int): width of each frame in pixels
        frame_height (int): height of each frame in pixels
        scale (int): integer scale factor to apply to frames
        colorkey (tuple|None): RGB color to treat as transparent when image lacks alpha

    Returns:
        list[pygame.Surface]: list of frames (possibly empty)
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    img = pygame.image.load(path)
    # try to keep per-pixel alpha if present
    try:
        img = img.convert_alpha()
    except Exception:
        img = img.convert()

    # If image has no alpha channel and a colorkey is provided, set it
    if img.get_alpha() is None and colorkey is not None:
        img.set_colorkey(colorkey)

    w, h = img.get_size()
    cols = w // frame_width if frame_width else 0
    rows = h // frame_height if frame_height else 0

    frames = []
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c * frame_width, r * frame_height, frame_width, frame_height)
            try:
                frame = img.subsurface(rect).copy()
            except Exception:
                continue

            # If no alpha, use mask to detect empty frames
            mask = pygame.mask.from_surface(frame)
            if mask.count() == 0:
                # skip fully empty frames
                continue

            if scale and scale != 1:
                target = (int(frame_width * scale), int(frame_height * scale))
                try:
                    frame = pygame.transform.smoothscale(frame, target)
                except Exception:
                    frame = pygame.transform.scale(frame, target)

            frames.append(frame)

    # If no frames found, fall back to whole image as single frame
    if not frames:
        single = img
        if scale and scale != 1:
            target = (int(w * scale), int(h * scale))
            try:
                single = pygame.transform.smoothscale(single, target)
            except Exception:
                single = pygame.transform.scale(single, target)
        frames = [single]

    return frames


class SpriteAnimator:
    def __init__(self, animations, default="idle", frame_duration=150, return_to_idle=True):
        """Control sprite animations.

        animations: dict[str, list[Surface]]
        frame_duration: ms per frame, or dict mapping animation->ms
        return_to_idle: whether to auto-return to default when non-loop finishes
        """
        self.animations = animations
        self.default = default
        self.frame_duration = frame_duration
        self.return_to_idle = return_to_idle

        self.current = default
        self.index = 0
        self.timer = 0.0  # ms
        self.looping = True
        self.finished = False

    def play(self, name, loop=False, reset=True):
        if name not in self.animations:
            name = self.default
        if reset or name != self.current:
            self.current = name
            self.index = 0
            self.timer = 0.0
            self.finished = False
            self.looping = loop

    def update(self, dt):
        # dt provided in seconds -> convert to ms
        ms = dt * 1000.0
        self.timer += ms

        # resolve duration for this animation
        dur = self.frame_duration
        if isinstance(self.frame_duration, dict):
            dur = self.frame_duration.get(self.current, 150)

        if dur <= 0:
            return

        frames = self.animations.get(self.current, [])
        if not frames:
            return

        while self.timer >= dur:
            self.timer -= dur
            self.index += 1
            if self.index >= len(frames):
                if self.looping or self.current == self.default:
                    self.index = 0
                else:
                    self.index = len(frames) - 1
                    self.finished = True
                    # optionally return to idle
                    if self.return_to_idle:
                        self.play(self.default, loop=True, reset=True)
                    break

    def get_image(self):
        frames = self.animations.get(self.current, [])
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
    """Draw frames side-by-side for debugging starting at (x,y) top-left."""
    px = x
    for img in frames:
        screen.blit(img, (px, y))
        px += img.get_width() + spacing
