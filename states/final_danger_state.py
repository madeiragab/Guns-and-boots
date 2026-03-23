import os
import random
import math
import pygame

from states.base_state import BaseState

W, H = 640, 360
FINAL_BOSSES_BASE = os.path.join("assets", "sprites", "Final Bosses")
MANDATORY_FINAL_BOSSES = ["Paulo"]
MANDATORY_BOSSES = ["Pablo"]


class FinalDangerState(BaseState):
    """Transition screen before the final boss battle."""

    def __init__(self, game):
        super().__init__(game)

    def on_enter(self):
        self._timer = 0.0
        self._duration = 3.0
        self._blink_timer = 0.0
        self._blink_visible = True
        self._flash_speed = 0.25

        # Preconstroi a geometria das rachaduras para a animacao parecer estavel e intencional.
        self._crack_origin = (W // 2, H // 2)
        self._main_cracks = []
        self._branch_cracks = []
        for _ in range(12):
            angle = random.uniform(0, 6.28318)
            length = random.randint(70, 220)
            end_x = int(self._crack_origin[0] + length * math.cos(angle))
            end_y = int(self._crack_origin[1] + length * math.sin(angle))
            end_x = max(0, min(W - 1, end_x))
            end_y = max(0, min(H - 1, end_y))
            self._main_cracks.append((self._crack_origin, (end_x, end_y)))

            branch_count = random.randint(1, 3)
            for _ in range(branch_count):
                t = random.uniform(0.25, 0.85)
                bx = int(self._crack_origin[0] + (end_x - self._crack_origin[0]) * t)
                by = int(self._crack_origin[1] + (end_y - self._crack_origin[1]) * t)
                ba = angle + random.uniform(-0.9, 0.9)
                bl = random.randint(18, 55)
                bex = int(bx + bl * math.cos(ba))
                bey = int(by + bl * math.sin(ba))
                bex = max(0, min(W - 1, bex))
                bey = max(0, min(H - 1, bey))
                self._branch_cracks.append(((bx, by), (bex, bey)))

    def handle_events(self, events):
        pass

    def update(self, dt):
        self._timer += dt
        self._blink_timer += dt
        if self._blink_timer >= self._flash_speed:
            self._blink_timer = 0.0
            self._blink_visible = not self._blink_visible

        if self._timer >= self._duration:
            self._start_final_boss_fight()

    def _get_undefeated_final_bosses(self):
        folders = []
        try:
            for name in os.listdir(FINAL_BOSSES_BASE):
                if os.path.isdir(os.path.join(FINAL_BOSSES_BASE, name)):
                    folders.append(name)
        except Exception:
            pass

        for name in MANDATORY_FINAL_BOSSES:
            if name not in folders:
                folders.append(name)

        defeated = getattr(self.game, "defeated_final_bosses", [])
        return [name for name in folders if name not in defeated]

    def _all_regular_bosses_defeated(self):
        bosses_base = os.path.join("assets", "sprites", "Bosses")
        bosses = []
        try:
            for name in os.listdir(bosses_base):
                if os.path.isdir(os.path.join(bosses_base, name)):
                    bosses.append(name)
        except Exception:
            pass

        for name in MANDATORY_BOSSES:
            if name not in bosses:
                bosses.append(name)

        defeated = set(getattr(self.game, "defeated_bosses", []))
        return all(name in defeated for name in bosses)

    def _start_final_boss_fight(self):
        from entities.final_boss import FinalBoss
        from states.battle_state import BattleState
        from states.credits_state import CreditsState
        from states.hub_state import HubState

        # Regra rigida: o chefe final so libera apos derrotar todos os chefes regulares.
        if not self._all_regular_bosses_defeated():
            self.game.state_manager.change(HubState(self.game))
            return

        available = self._get_undefeated_final_bosses()
        if not available:
            if hasattr(self.game, "final_boss_retry_target"):
                self.game.final_boss_retry_target = None
            self.game.complete_game()
            self.game.state_manager.change(CreditsState(self.game))
            return

        retry_target = getattr(self.game, "final_boss_retry_target", None)
        if retry_target in available:
            folder = retry_target
        else:
            folder = random.choice(available)

        self.game.final_boss_retry_target = None
        final_boss = FinalBoss(folder, self.game.player)
        self.game.player.reset_for_battle()
        self.game.state_manager.change(BattleState(self.game, self.game.player, final_boss))

    def draw(self, screen):
        screen.fill((95, 0, 0))

        progress = min(1.0, self._timer / self._duration)
        reveal_count = int(len(self._main_cracks) * progress)
        reveal_branches = int(len(self._branch_cracks) * progress)

        # Pulsos de flash sutis para imitar ondas de impacto.
        pulse_alpha = int((0.35 + 0.65 * progress) * 80)
        pulse = pygame.Surface((W, H), pygame.SRCALPHA)
        pulse.fill((255, 255, 255, pulse_alpha if self._blink_visible else pulse_alpha // 2))
        screen.blit(pulse, (0, 0))

        crack_color = (230, 230, 230)
        branch_color = (170, 170, 170)
        for start, end in self._main_cracks[:reveal_count]:
            pygame.draw.line(screen, crack_color, start, end, 2)
        for start, end in self._branch_cracks[:reveal_branches]:
            pygame.draw.line(screen, branch_color, start, end, 1)

        # Blocos de vinheta escura nos cantos para reforcar a sensacao de tela quebrada.
        shard = pygame.Surface((W, H), pygame.SRCALPHA)
        corner_alpha = int(85 + progress * 90)
        pygame.draw.polygon(shard, (15, 0, 0, corner_alpha), [(0, 0), (180, 0), (0, 120)])
        pygame.draw.polygon(shard, (15, 0, 0, corner_alpha), [(W, 0), (W - 180, 0), (W, 120)])
        pygame.draw.polygon(shard, (15, 0, 0, corner_alpha), [(0, H), (170, H), (0, H - 110)])
        pygame.draw.polygon(shard, (15, 0, 0, corner_alpha), [(W, H), (W - 170, H), (W, H - 110)])
        screen.blit(shard, (0, 0))

        if self._blink_visible:
            font = pygame.font.SysFont("Courier New", 56, bold=True)
            text = font.render("BOSS FINAL", True, (255, 255, 255))
            screen.blit(text, (W // 2 - text.get_width() // 2, H // 2 - text.get_height() // 2))
