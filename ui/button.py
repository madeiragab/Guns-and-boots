import pygame

WHITE    = (255, 255, 255)
GRAY     = (60,  60,  60)
SELECTED = (180, 180, 60)
BLACK    = (0,   0,   0)
DISABLED_BG = (40, 40, 40)
DISABLED_FG = (90, 90, 90)


class Button:
    """A simple text menu button."""

    def __init__(self, x, y, width, height, text):
        self.rect     = pygame.Rect(x, y, width, height)
        self.text     = text
        self.active   = False     # highlighted / selected
        self.disabled = False     # grayed out / unclickable

    def draw(self, screen, font):
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
