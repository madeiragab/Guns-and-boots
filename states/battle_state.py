import pygame
from states.base_state import BaseState
from ui.button    import Button
from ui.healthbar import HealthBar
from ui.logbox    import LogBox
from systems.combat import resolve_action
from systems.ai     import choose_action
import os
import random

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

# Action menu  (bottom-right) -- kept for input layout though not drawn
MENU_X     = W // 2 + 20
MENU_Y     = H - 130
BTN_W, BTN_H = 170, 22
BTN_GAP    = 4

# Log box (not drawn currently)
LOG_X, LOG_Y = 10, H - 130
LOG_W, LOG_H = W // 2 - 20, 90

class BattleState(BaseState):
    """
    BATTLE screen — full turn-based combat loop.
    """

    def __init__(self, game, player, enemy):
        super().__init__(game)
        self.player = player
        self.enemy = enemy

    def on_enter(self):
        self._turn = "player"
        self._selected = 0
        self._waiting = False
        self._wait_timer = 0.0

        # Buttons (kept for input handling but not drawn)
        self._buttons = [
            Button(MENU_X, MENU_Y + i * (BTN_H + BTN_GAP), BTN_W, BTN_H, label)
            for i, label in enumerate(ACTIONS)
        ]
        self._update_selection()

        # Health bars for each combatant; will be positioned above sprites
        bar_w, bar_h = 120, 12
        self._enemy_hp_bar = HealthBar(0, 0, bar_w, bar_h, self.enemy.max_hp, label="ENEMY HP", dynamic_color=True)
        self._player_hp_bar = HealthBar(0, 0, bar_w, bar_h, self.player.max_hp, label="PLAYER HP", dynamic_color=True)

        # Log kept but not drawn
        self._log = LogBox(LOG_X, LOG_Y, LOG_W, LOG_H, max_lines=5)
        self._log.add("Battle started!")

        try:
            self.player.play("idle")
        except Exception:
            pass

        # Pick a random field background from assets/sprites/field (walk recursively)
        try:
            base_field = os.path.join("assets", "sprites", "field")
            choices = []
            for root, dirs, files in os.walk(base_field):
                for fn in files:
                    if fn.lower().endswith((".png", ".jpg", ".jpeg")):
                        choices.append(os.path.join(root, fn))

            if choices:
                pick = random.choice(choices)
                # Avoid convert_alpha/convert here in case display isn't fully initialized;
                # pygame.image.load alone returns a usable Surface.
                surf = pygame.image.load(pick)
                # scale to fill screen while preserving aspect ratio
                sw, sh = surf.get_size()
                scale = max(W / sw, H / sh)
                nw, nh = int(sw * scale), int(sh * scale)
                surf = pygame.transform.smoothscale(surf, (nw, nh))
                # center crop to window
                x = (nw - W) // 2
                y = (nh - H) // 2
                self._field_surf = surf.subsurface((x, y, W, H)).copy()
                print(f"[BattleState] picked field background: {pick}")
            else:
                self._field_surf = None
        except Exception:
            self._field_surf = None

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
                elif event.key == pygame.K_LEFT:
                    self._selected = (self._selected - 1) % len(ACTIONS)
                    self._update_selection()
                elif event.key == pygame.K_RIGHT:
                    self._selected = (self._selected + 1) % len(ACTIONS)
                    self._update_selection()
                elif event.key == pygame.K_RETURN:
                    self._player_act(ACTIONS[self._selected].lower().replace(" ", "_"))

    # ------------------------------------------------------------------
    def _player_act(self, action):
        action = action.replace("take_cover", "cover")
        # play matching animation
        anim_map = {
            "shoot": "shoot",
            "cover": "cover",
            "overcharge": "shoot",
            "medkit": "medkit",
        }
        try:
            self.player.play(anim_map.get(action, "idle"))
        except Exception:
            pass

        # record enemy HP to detect if damage was applied
        try:
            enemy_before_hp = self.enemy.hp
        except Exception:
            enemy_before_hp = None

        logs = resolve_action(self.player, self.enemy, action)
        for line in logs:
            self._log.add(line)

        # play enemy damage animation if HP decreased
        try:
            if enemy_before_hp is not None and self.enemy.hp < enemy_before_hp:
                try:
                    self.enemy.play("damage")
                except Exception:
                    pass
        except Exception:
            pass

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
        # play enemy animation for this action
        anim_map = {
            "shoot": "shoot",
            "cover": "cover",
            "overcharge": "shoot",
            "medkit": "medkit",
        }
        try:
            self.enemy.play(anim_map.get(action, "idle"))
        except Exception:
            pass

        logs = resolve_action(self.enemy, self.player, action)
        for line in logs:
            self._log.add(line)

        if not self.player.is_alive():
            self._end_battle("lose")
            return

        # If enemy attacked, show player damage animation
        if action in ("shoot", "overcharge"):
            try:
                self.player.play("damage")
            except Exception:
                pass

        self._turn = "player"

    # ------------------------------------------------------------------
    def _end_battle(self, outcome):
        self._turn = "gameover"
        from states.result_state import ResultState
        self.game.state_manager.change(ResultState(self.game, outcome))

    # ------------------------------------------------------------------
    def update(self, dt):
        # update player animation
        try:
            self.player.update(dt)
        except Exception:
            pass
        # update enemy animation
        try:
            self.enemy.update(dt)
        except Exception:
            pass

        if self._waiting:
            self._wait_timer += dt
            if self._wait_timer >= 0.80:
                self._waiting = False
                self._enemy_act()

    # ------------------------------------------------------------------
    def draw(self, screen):
        # Draw field background if available, otherwise full black background.
        if getattr(self, "_field_surf", None) is not None:
            try:
                screen.blit(self._field_surf, (0, 0))
            except Exception:
                screen.fill((0, 0, 0))
        else:
            screen.fill((0, 0, 0))

        font_small = pygame.font.SysFont("Courier New", 12)

        # Optional: draw player sprite in the left area (behind where UI used to be)
        try:
            # player at bottom-left corner (feet anchored) moved slightly right
            px = 80
            py = H - 10
            # draw sprite and also render player name above the sprite
            img = None
            try:
                img = self.player.animator.get_image()
            except Exception:
                img = None

            # draw sprite (uses midbottom anchoring)
            self.player.draw(screen, (px, py))

            # draw name above sprite
            if img is not None:
                rect = img.get_rect(midbottom=(px, py))
                name_font = pygame.font.SysFont("Courier New", 14, bold=True)
                name_surf = name_font.render(self.player.name, True, (50, 200, 80))
                name_r = name_surf.get_rect(midbottom=(rect.centerx, rect.top - 6))
                screen.blit(name_surf, name_r)
        except Exception:
            pass

        # Place HP bars: PLAYER on the left, ENEMY on the right
        try:
            self._player_hp_bar.rect.topleft = (ENEMY_BAR_X, ENEMY_BAR_Y)
            self._player_hp_bar.draw(screen, font_small, self.player.hp)
        except Exception:
            pass

        try:
            self._enemy_hp_bar.rect.topright = (W - 10, ENEMY_BAR_Y)
            self._enemy_hp_bar.draw(screen, font_small, self.enemy.hp)
        except Exception:
            pass

        # Draw enemy sprite at bottom-right (feet anchored)
        try:
            ex = W - 80
            ey = H - 10
            # enemy animator is updated in update(dt)

            try:
                self.enemy.draw(screen, (ex, ey))
                # draw enemy name above sprite
                img = None
                try:
                    img = self.enemy.animator.get_image()
                except Exception:
                    img = None

                if img is not None:
                    rect = img.get_rect(midbottom=(ex, ey))
                    name_font = pygame.font.SysFont("Courier New", 14, bold=True)
                    lbl = name_font.render(self.enemy.name, True, (200, 40, 40))
                    lbl_r = lbl.get_rect(midbottom=(rect.centerx, rect.top - 6))
                    screen.blit(lbl, lbl_r)
            except Exception:
                # fallback placeholder box
                box_w, box_h = 80, 120
                surf = pygame.Surface((box_w, box_h))
                surf.fill((40, 40, 40))
                rect = surf.get_rect(midbottom=(ex, ey))
                pygame.draw.rect(surf, (80, 80, 80), surf.get_rect(), 2)
                screen.blit(surf, rect)
                name_font = pygame.font.SysFont("Courier New", 14, bold=True)
                lbl = name_font.render(self.enemy.name, True, (200, 40, 40))
                lbl_r = lbl.get_rect(midbottom=(rect.centerx, rect.top - 6))
                screen.blit(lbl, lbl_r)
        except Exception:
            pass

        # Draw buttons centered at bottom (compact row)
        try:
            btn_count = len(self._buttons)
            total_w = BTN_W * btn_count + BTN_GAP * (btn_count - 1)
            start_x = W // 2 - total_w // 2
            y = H - BTN_H - 10
            for i, btn in enumerate(self._buttons):
                bx = start_x + i * (BTN_W + BTN_GAP)
                btn.rect.topleft = (bx, y)
                btn.draw(screen, pygame.font.SysFont("Courier New", 13))
        except Exception:
            pass
