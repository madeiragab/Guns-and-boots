import os
import sys
import pygame
from core.game import Game


def is_mobile_arg():
    return '--mobile' in sys.argv or os.environ.get('MOBILE', '') in ('1', 'true', 'True')


if __name__ == "__main__":
    pygame.init()
    mobile = is_mobile_arg()
    game = Game(mobile=mobile)
    try:
        game.run()
    finally:
        pygame.quit()
