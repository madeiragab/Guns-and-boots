import pygame

WHITE = (255, 255, 255)
BLACK = (0,   0,   0)


def _lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def _hp_color(ratio):
    """Green → yellow → red based on HP fraction."""
    if ratio > 0.5:
        return _lerp((50, 200, 70), (220, 200, 0), 1.0 - (ratio - 0.5) * 2)
    else:
        return _lerp((220, 200, 0), (200, 35, 35), 1.0 - ratio * 2)


class HealthBar:
    """
    Polished HP / resource bar.

    Parameters
    ----------
    dynamic_color : bool
        If True, fill shifts green → yellow → red with the HP ratio.
        If False, uses the fixed ``color`` supplied at construction.
    """

    def __init__(self, x, y, width, height, max_value,
                 color=(50, 200, 70), label="HP", dynamic_color=True):
        self.rect          = pygame.Rect(x, y, width, height)
        self.max_value     = max_value
        self._base_color   = color
        self.label         = label
        self.dynamic_color = dynamic_color

    def draw(self, screen, font, current_value):
        ratio = max(0.0, min(1.0, current_value / self.max_value))
        color = _hp_color(ratio) if self.dynamic_color else self._base_color

        # 1. bandeja externa de sombra
        shadow = self.rect.inflate(4, 4)
        pygame.draw.rect(screen, (15, 15, 15), shadow, border_radius=3)

        # 2. bandeja vazia
        pygame.draw.rect(screen, (35, 35, 35), self.rect, border_radius=2)

        # 3. porcao preenchida
        fill_w = max(0, int(self.rect.width * ratio))
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y,
                                    fill_w, self.rect.height)
            pygame.draw.rect(screen, color, fill_rect, border_radius=2)

            # faixa de brilho - 2 px do topo, levemente mais clara
            hl = _lerp(color, WHITE, 0.40)
            hl_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 1,
                                  max(0, fill_w - 4), 2)
            if hl_rect.width > 0:
                pygame.draw.rect(screen, hl, hl_rect)

        # 4. marcacoes em 25 / 50 / 75 %
        for pct in (0.25, 0.50, 0.75):
            tx = self.rect.x + int(self.rect.width * pct)
            pygame.draw.line(screen, (55, 55, 55),
                             (tx, self.rect.y + 1),
                             (tx, self.rect.bottom - 2), 1)

        # 5. borda
        pygame.draw.rect(screen, (110, 110, 110), self.rect, 1, border_radius=2)

        # 6. rotulo + valor numerico acima da barra
        text_surf = font.render(
            f"{self.label}  {int(current_value)} / {int(self.max_value)}",
            True, WHITE
        )
        screen.blit(text_surf,
                    (self.rect.x, self.rect.y - text_surf.get_height() - 3))
