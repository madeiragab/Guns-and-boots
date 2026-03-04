import pygame

WHITE = (255, 255, 255)
GRAY  = (40,  40,  40)
BLACK = (0,   0,   0)
DIM   = (130, 130, 130)


class LogBox:
    """Scrolling text log that keeps the last N lines."""

    def __init__(self, x, y, width, height, max_lines=6):
        self.rect      = pygame.Rect(x, y, width, height)
        self.max_lines = max_lines
        self.lines     = []

    def add(self, text):
        self.lines.append(text)
        if len(self.lines) > self.max_lines:
            self.lines.pop(0)

    def clear(self):
        self.lines = []

    def draw(self, screen, font):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 1)

        line_h = font.get_height() + 2
        for i, line in enumerate(self.lines):
            surf = font.render(line, True, DIM if i < len(self.lines) - 1 else WHITE)
            screen.blit(surf, (self.rect.x + 4,
                               self.rect.y + 4 + i * line_h))
