import pygame


_FONT_CACHE = {}


def get_font(name, size, bold=False, italic=False):
    key = (name, size, bold, italic)
    font = _FONT_CACHE.get(key)
    if font is None:
        font = pygame.font.SysFont(name, size, bold=bold, italic=italic)
        _FONT_CACHE[key] = font
    return font