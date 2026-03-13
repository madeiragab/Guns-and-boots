"""Headless smoke-test: boots the game for a few frames and exits.

Usage (from project root):
    python tools/run_test.py
"""
import sys
import os

# Ensure project root is on sys.path and CWD is root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
pygame.init()

try:
    from core.game import Game
except Exception as e:
    print('IMPORT_ERR', e)
    pygame.quit()
    sys.exit(1)

try:
    g = Game()
    for i in range(3):
        dt = g.clock.tick(60) / 1000.0
        events = pygame.event.get()
        g.state_manager.handle_events(events)
        g.state_manager.update(dt)
        g.screen.fill((0, 0, 0))
        g.state_manager.draw(g.screen)
        pygame.display.flip()
    print('RUN_OK')
except Exception as e:
    print('RUN_ERR', e)
finally:
    pygame.quit()
