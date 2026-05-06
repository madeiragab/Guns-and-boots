import pygame
from ui.font_cache import get_font

WHITE    = (255, 255, 255)
GRAY     = (60,  60,  60)
SELECTED = (180, 180, 60)
BLACK    = (0,   0,   0)
DISABLED_BG = (40, 40, 40)
DISABLED_FG = (90, 90, 90)


class Button:
    """A simple text menu button.

    The `draw` method accepts an optional `font`. When omitted, a cached
    font from `ui.font_cache.get_font` is chosen based on the button height
    to avoid recreating fonts each frame and to keep visual consistency.
    """

    def __init__(self, x, y, width, height, text):
        self.rect     = pygame.Rect(x, y, width, height)
        self.text     = text
        self.active   = False     # destacado / selecionado
        self.disabled = False     # acinzentado / nao clicavel

    def draw(self, screen, font=None):
        # Choose a cached font if none provided. Size is derived from height.
        if font is None:
            size = max(12, self.rect.height - 8)
            font = get_font("Courier New", size, bold=self.active)

        if self.disabled:
            pygame.draw.rect(screen, DISABLED_BG, self.rect)
            pygame.draw.rect(screen, DISABLED_FG, self.rect, 1)
            surf = font.render(f"X  {self.text}", True, DISABLED_FG)
        else:
            bg = SELECTED if self.active else GRAY
            fg = BLACK    if self.active else WHITE
            pygame.draw.rect(screen, bg, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 1)
            surf = font.render(self.text, True, fg)

        tx = self.rect.x + (self.rect.width  - surf.get_width())  // 2
        ty = self.rect.y + (self.rect.height - surf.get_height()) // 2
        screen.blit(surf, (tx, ty))

    def handle_event(self, event, mobile=False):
        """Return True if this button was activated by the given event.

        On desktop this reacts to mouse clicks inside the rect. On mobile
        we allow a slightly larger hit area for easier tapping.
        """
        if self.disabled:
            return False
        if event.type != pygame.MOUSEBUTTONDOWN:
            return False
        pt = event.pos
        if mobile:
            hit = self.rect.inflate(12, 12).collidepoint(pt)
        else:
            hit = self.rect.collidepoint(pt)
        return bool(hit)
