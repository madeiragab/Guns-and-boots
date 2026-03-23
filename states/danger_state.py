import os
import random
import pygame
from states.base_state import BaseState

W, H = 640, 360
MANDATORY_BOSSES = ["Pablo"]


class DangerState(BaseState):
    """Red screen with flashing DANGER text, then transitions to boss battle."""

    def __init__(self, game):
        super().__init__(game)

    def on_enter(self):
        self._timer = 0.0
        self._duration = 3.0
        self._blink_timer = 0.0
        self._blink_visible = True
        self._flash_speed = 0.3

    def handle_events(self, events):
        pass  # sem entrada durante a tela de perigo

    def update(self, dt):
        self._timer += dt
        self._blink_timer += dt
        if self._blink_timer >= self._flash_speed:
            self._blink_timer = 0.0
            self._blink_visible = not self._blink_visible

        if self._timer >= self._duration:
            self._start_boss_fight()

    def _get_undefeated_bosses(self):
        from entities.boss import BOSSES_BASE
        boss_folders = []
        try:
            for name in os.listdir(BOSSES_BASE):
                if os.path.isdir(os.path.join(BOSSES_BASE, name)):
                    boss_folders.append(name)
        except Exception:
            pass

        # Mantem Pablo disponivel no grupo de chefes mesmo como personagem inicial.
        for name in MANDATORY_BOSSES:
            if name not in boss_folders:
                boss_folders.append(name)

        defeated = getattr(self.game, 'defeated_bosses', [])
        return [b for b in boss_folders if b not in defeated]

    def _start_boss_fight(self):
        from entities.boss import Boss
        from states.battle_state import BattleState

        available = self._get_undefeated_bosses()
        if not available:
            from states.hub_state import HubState
            self.game.state_manager.change(HubState(self.game))
            return

        folder = random.choice(available)
        boss = Boss(folder)
        self.game.player.reset_for_battle()
        self.game.state_manager.change(BattleState(self.game, self.game.player, boss))

    def draw(self, screen):
        screen.fill((140, 0, 0))

        if self._blink_visible:
            font = pygame.font.SysFont("Courier New", 64, bold=True)
            text = font.render("PERIGO", True, (255, 255, 255))
            screen.blit(text, (W // 2 - text.get_width() // 2, H // 2 - text.get_height() // 2))
