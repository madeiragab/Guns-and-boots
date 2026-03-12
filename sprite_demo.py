import pygame
import sys
from core.sprite_animator import load_animations_from_folders, SpriteAnimator, draw


W, H = 640, 360


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Sprite Animator Demo")
    clock = pygame.time.Clock()

    base = "assets/sprites/Player"
    # Standardize sprite visual size (w, h) so animations don't 'jump'.
    # Adjust target_size to the desired final size in pixels.
    target_size = (160, 160)
    animations = load_animations_from_folders(base, scale=1, target_size=target_size)

    if not animations:
        print("No animations found in", base)
        pygame.quit()
        sys.exit(1)

    animator = SpriteAnimator(animations, default="idle", fps=12, return_to_idle=True)

    # key mapping
    key_map = {
        pygame.K_1: "idle",
        pygame.K_2: "shoot",
        pygame.K_3: "cover",
        pygame.K_4: "damage",
    }

    font = pygame.font.SysFont("Courier New", 14)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in key_map:
                    name = key_map[event.key]
                    loop = (name == "idle")
                    # non-idle animations play once and return to idle
                    animator.play(name, loop=loop, reset=True)

        animator.update(dt)

        screen.fill((12, 12, 12))

        # draw instructions
        instr = font.render("1: idle  2: shoot  3: cover  4: damage  ESC: quit", True, (200, 200, 200))
        screen.blit(instr, (10, 10))

        # draw current animation name
        name_txt = font.render(f"Anim: {animator.current}", True, (200, 200, 200))
        screen.blit(name_txt, (10, 30))

        # draw sprite at center-bottom-ish
        img = animator.get_image()
        draw(screen, img, (W // 2, H // 2 + 60))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
