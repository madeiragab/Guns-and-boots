import pygame
from states.base_state import BaseState
from ui.button    import Button
from ui.healthbar import HealthBar
from ui.logbox    import LogBox
from systems.combat import resolve_action
from systems.ai     import choose_action

WHITE  = (255, 255, 255)
GRAY   = (80,  80,  80)
BLACK  = (0,   0,   0)
RED    = (200, 40,  40)
ORANGE = (210, 130, 0)

ACTIONS = ["SHOOT", "TAKE COVER", "OVERCHARGE", "MEDKIT"]

# ── Layout constants ──────────────────────────────────────────────────
W, H = 640, 360

# Panels
PANEL_W       = W // 2 - 10
ENEMY_PANEL_H = 68
PLAYER_PANEL_H = 90

# Enemy panel  (top-left)
ENEMY_PANEL_Y = 0
ENEMY_BAR_X   = 12
ENEMY_BAR_Y   = ENEMY_PANEL_Y + 34    # below name label
ENEMY_BAR_W   = 260
ENEMY_BAR_H   = 16

# Player panel (bottom-left)
PLAYER_PANEL_Y = H - PLAYER_PANEL_H
PLAYER_BAR_X   = 12
PLAYER_BAR_Y   = PLAYER_PANEL_Y + 30
PLAYER_BAR_W   = 260
PLAYER_BAR_H   = 16
HEAT_BAR_Y     = PLAYER_PANEL_Y + 64
HEAT_BAR_W     = 180
HEAT_BAR_H     = 10

# Action menu  (bottom-right)
MENU_X     = W // 2 + 20
MENU_Y     = H - 130
BTN_W, BTN_H = 170, 22
BTN_GAP    = 4

# Log box
LOG_X, LOG_Y = 10, H - 130
LOG_W, LOG_H = W // 2 - 20, 90


class BattleState(BaseState):
    """
    BATTLE screen — full turn-based combat loop.
    """

    def __init__(self, game, player, enemy):
        super().__init__(game)
        self.player = player
        self.enemy  = enemy

    def on_enter(self):
        self._turn     = "player"       # "player" | "enemy" | "gameover"
        self._selected = 0
        self._waiting  = False          # True while enemy "thinking" delay
        self._wait_timer = 0.0

        # Buttons
        self._buttons = [
            Button(MENU_X, MENU_Y + i * (BTN_H + BTN_GAP), BTN_W, BTN_H, label)
            for i, label in enumerate(ACTIONS)
        ]
        self._update_selection()

        # Bars
        self._enemy_hp_bar = HealthBar(
            ENEMY_BAR_X, ENEMY_BAR_Y, ENEMY_BAR_W, ENEMY_BAR_H,
            self.enemy.max_hp, label="HP", dynamic_color=True
        )
        self._player_hp_bar = HealthBar(
            PLAYER_BAR_X, PLAYER_BAR_Y, PLAYER_BAR_W, PLAYER_BAR_H,
            self.player.max_hp, label="HP", dynamic_color=True
        )
        self._heat_bar = HealthBar(
            PLAYER_BAR_X, HEAT_BAR_Y, HEAT_BAR_W, HEAT_BAR_H,
            10, color=ORANGE, label="HEAT", dynamic_color=False
        )

        # Log
        self._log = LogBox(LOG_X, LOG_Y, LOG_W, LOG_H, max_lines=5)
        self._log.add("Battle started!")

    # ------------------------------------------------------------------
    def _update_selection(self):
        for i, btn in enumerate(self._buttons):
            btn.active = (i == self._selected)

    # ------------------------------------------------------------------
    def handle_events(self, events):
        if self._turn != "player":
            return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self._selected = (self._selected - 1) % len(ACTIONS)
                    self._update_selection()
                elif event.key == pygame.K_DOWN:
                    self._selected = (self._selected + 1) % len(ACTIONS)
                    self._update_selection()
                elif event.key == pygame.K_RETURN:
                    self._player_act(ACTIONS[self._selected].lower().replace(" ", "_"))

    # ------------------------------------------------------------------
    def _player_act(self, action):
        action = action.replace("take_cover", "cover")
        logs = resolve_action(self.player, self.enemy, action)
        for line in logs:
            self._log.add(line)

        if not self.enemy.is_alive():
            self._end_battle("win")
            return

        # Enemy turn after a short delay
        self._turn       = "enemy"
        self._waiting    = True
        self._wait_timer = 0.0

    # ------------------------------------------------------------------
    def _enemy_act(self):
        action = choose_action(self.enemy, self.player)
        logs   = resolve_action(self.enemy, self.player, action)
        for line in logs:
            self._log.add(line)

        if not self.player.is_alive():
            self._end_battle("lose")
            return

        self._turn = "player"

    # ------------------------------------------------------------------
    def _end_battle(self, outcome):
        self._turn = "gameover"
        from states.result_state import ResultState
        self.game.state_manager.change(ResultState(self.game, outcome))

    # ------------------------------------------------------------------
    def update(self, dt):
        if self._waiting:
            self._wait_timer += dt
            if self._wait_timer >= 0.80:
                self._waiting = False
                self._enemy_act()

    # ------------------------------------------------------------------
    def draw(self, screen):
        font       = pygame.font.SysFont("Courier New", 14)
        font_name  = pygame.font.SysFont("Courier New", 16, bold=True)
        font_small = pygame.font.SysFont("Courier New", 12)
        font_btn   = pygame.font.SysFont("Courier New", 13)

        # ── Enemy panel background ────────────────────────────────────
        pygame.draw.rect(screen, (22, 10, 10),
                         (0, ENEMY_PANEL_Y, PANEL_W, ENEMY_PANEL_H))
        pygame.draw.line(screen, (80, 20, 20),
                         (0, ENEMY_PANEL_H - 1), (PANEL_W, ENEMY_PANEL_H - 1))

        enemy_lbl = font_name.render(self.enemy.name, True, RED)
        screen.blit(enemy_lbl, (ENEMY_BAR_X, ENEMY_PANEL_Y + 8))
        self._enemy_hp_bar.draw(screen, font_small, self.enemy.hp)

        if self.enemy.cover:
            cov = font_small.render("[ IN COVER ]", True, (100, 200, 255))
            screen.blit(cov, (ENEMY_BAR_X + ENEMY_BAR_W + 8, ENEMY_BAR_Y + 2))

        # ── Enemy "sprite" placeholder ────────────────────────────────
        box_rect = pygame.Rect(W // 2 - 50, H // 2 - 60, 100, 100)
        pygame.draw.rect(screen, (30, 30, 30), box_rect)
        pygame.draw.rect(screen, GRAY, box_rect, 1)
        sp = font_small.render(self.enemy.name, True, GRAY)
        screen.blit(sp, (box_rect.centerx - sp.get_width() // 2,
                         box_rect.centery - sp.get_height() // 2))

        # ── Player panel background ───────────────────────────────────
        pygame.draw.rect(screen, (10, 18, 10),
                         (0, PLAYER_PANEL_Y, PANEL_W, PLAYER_PANEL_H))
        pygame.draw.line(screen, (20, 80, 20),
                         (0, PLAYER_PANEL_Y), (PANEL_W, PLAYER_PANEL_Y))

        player_lbl = font_name.render(self.player.name, True, WHITE)
        screen.blit(player_lbl, (PLAYER_BAR_X, PLAYER_PANEL_Y + 8))
        self._player_hp_bar.draw(screen, font_small, self.player.hp)
        self._heat_bar.draw(screen, font_small, self.player.heat)

        # Medkits (right of HEAT bar)
        mk_text = "[ + ] " * self.player.medkits if self.player.medkits else "none"
        mk = font_small.render(f"MEDKIT: {mk_text}", True, (180, 180, 180))
        screen.blit(mk, (PLAYER_BAR_X + HEAT_BAR_W + 12, HEAT_BAR_Y - 1))

        if self.player.cover:
            cov = font_small.render("[ IN COVER ]", True, (100, 200, 255))
            screen.blit(cov, (PLAYER_BAR_X + PLAYER_BAR_W + 8, PLAYER_BAR_Y + 2))

        # ── Action buttons ───────────────────────────────────────────
        turn_lbl = font.render(
            "YOUR TURN" if self._turn == "player" else "ENEMY TURN...",
            True, WHITE
        )
        screen.blit(turn_lbl, (MENU_X, MENU_Y - 20))

        for btn in self._buttons:
            btn.draw(screen, font_btn)

        # ── Log box ───────────────────────────────────────────────────
        self._log.draw(screen, font_small)

        # ── Hint ──────────────────────────────────────────────────────
        hint = font_small.render("↑↓ select   ENTER confirm", True, GRAY)
        screen.blit(hint, (MENU_X, MENU_Y + len(ACTIONS) * (BTN_H + BTN_GAP) + 4))
