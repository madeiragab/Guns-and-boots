"""Interactive sprite animation viewer.

Usage (from project root):
    python tools/sprite_demo.py

Keys 1-9 trigger different animations. ESC quits.
"""
import sys
import os

# Ensure project root is on sys.path and CWD is root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame
from core.sprite_animator import load_animations_from_folders, SpriteAnimator, draw

W, H = 640, 360


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Sprite Animator Demo")
    clock = pygame.time.Clock()

    base = os.path.join("assets", "sprites", "Players", "Player 1")
    target_size = (160, 160)
    animations = load_animations_from_folders(base, scale=1, target_size=target_size)

    if not animations:
        print("No animations found in", base)
        pygame.quit()
        sys.exit(1)

    animator = SpriteAnimator(animations, default="idle", fps=12, return_to_idle=True)

    anim_names = sorted(animations.keys())
    print("Available animations:", anim_names)

    key_map = {}
    for i, name in enumerate(anim_names):
        key = getattr(pygame, f"K_{i + 1}", None)
        if key:
            key_map[key] = name

    loop = False
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_l:
                    loop = not loop
                    print("Loop:", loop)
                elif event.key in key_map:
                    name = key_map[event.key]
                    print(f"Playing: {name}  loop={loop}")
                    animator.play(name, loop=loop, reset=True)

        animator.update(dt)
        screen.fill((30, 30, 30))
        img = animator.get_image()
        if img:
            rect = img.get_rect(center=(W // 2, H // 2))
            screen.blit(img, rect)

        font = pygame.font.SysFont("Courier New", 13)
        hints = [f"{i + 1}: {n}" for i, n in enumerate(anim_names)]
        hints.append("L: toggle loop  |  ESC: quit")
        for j, h in enumerate(hints):
            screen.blit(font.render(h, True, (180, 180, 180)), (10, 10 + j * 18))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
