import pygame
from states.base_state import BaseState
from ui.button    import Button
from ui.healthbar import HealthBar
from ui.logbox    import LogBox
from systems.combat import resolve_action
from systems.ai     import choose_action
from entities.projectile import Projectile
import os
import random

WHITE  = (255, 255, 255)
GRAY   = (80,  80,  80)
BLACK  = (0,   0,   0)
RED    = (200, 40,  40)
ORANGE = (210, 130, 0)

ACTIONS = ["ATIRAR", "COBERTURA", "ESPECIAL", "MEDKIT"]

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
        self._final_stand_used = False
        self._final_stand_warning_active = False
        self._final_stand_warning_timer = 0.0
        self._final_stand_warning_duration = 1.8
        self._transform_anim_active = False
        self._transform_anim_timer = 0.0
        self._transform_anim_duration = 1.25
        self._projectiles = []  # active projectiles on screen

        # Sprite positions (used for projectile start/end)
        self._player_pos = (80, H - 10)
        self._enemy_pos = (W - 80, H - 10)

        # Buttons (kept for input handling but not drawn)
        self._buttons = [
            Button(MENU_X, MENU_Y + i * (BTN_H + BTN_GAP), BTN_W, BTN_H, label)
            for i, label in enumerate(ACTIONS)
        ]
        self._update_disabled_buttons()
        self._update_selection()

        # Health bars for each combatant; will be positioned above sprites
        bar_w, bar_h = 120, 12
        self._enemy_hp_bar = HealthBar(0, 0, bar_w, bar_h, self.enemy.max_hp, label="HP INIMIGO", dynamic_color=True)
        self._player_hp_bar = HealthBar(0, 0, bar_w, bar_h, self.player.max_hp, label="HP JOGADOR", dynamic_color=True)

        # Log kept but not drawn
        self._log = LogBox(LOG_X, LOG_Y, LOG_W, LOG_H, max_lines=5)
        self._log.add("Batalha iniciada!")

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
            btn.active = (i == self._selected) and not btn.disabled

    def _update_disabled_buttons(self):
        """Mark buttons as disabled based on current player state."""
        for i, btn in enumerate(self._buttons):
            action = ACTIONS[i]
            if action == "MEDKIT":
                btn.disabled = self.player.medkits <= 0
            elif action == "ESPECIAL":
                btn.disabled = getattr(self.player, 'special_cooldown', 0) > 0
            else:
                btn.disabled = False

    def _skip_to_valid(self, direction):
        """Move selection in direction (+1 or -1), skipping disabled buttons."""
        for _ in range(len(ACTIONS)):
            self._selected = (self._selected + direction) % len(ACTIONS)
            if not self._buttons[self._selected].disabled:
                return
        # All disabled fallback (shouldn't happen)
        self._selected = 0

    # ------------------------------------------------------------------
    def handle_events(self, events):
        if self._turn != "player":
            return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_LEFT):
                    self._skip_to_valid(-1)
                    self._update_selection()
                elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                    self._skip_to_valid(1)
                    self._update_selection()
                elif event.key == pygame.K_RETURN:
                    if not self._buttons[self._selected].disabled:
                        self._player_act(ACTIONS[self._selected].lower().replace(" ", "_"))

    # ------------------------------------------------------------------
    def _player_act(self, action):
        action = action.replace("atirar", "shoot").replace("cobertura", "cover").replace("especial", "special")
        # play matching animation
        anim_map = {
            "shoot": "shoot",
            "cover": "cover",
            "special": "special",
            "medkit": "medkit",
        }
        try:
            self.player.play(anim_map.get(action, "idle"))
        except Exception:
            pass

        # For shoot/special, spawn a projectile first, then resolve on hit
        if action in ("shoot", "special"):
            if action == "special":
                self.game.play_special_sfx()
            else:
                self.game.play_bullet_sfx()
            bullet_frames = (self.player.special_bullet_frames
                             if action == "special"
                             else self.player.bullet_frames)
            # Projectile flies from player to enemy
            start = (self._player_pos[0] + 40, self._player_pos[1] - 80)
            end = (self._enemy_pos[0] - 40, self._enemy_pos[1] - 80)

            def on_hit():
                self._resolve_player_attack(action)

            proj = Projectile(bullet_frames, start, end, duration=0.35, on_hit=on_hit)
            self._projectiles.append(proj)
            self._turn = "projectile"
        else:
            # Non-projectile actions resolve immediately
            logs = resolve_action(self.player, self.enemy, action)
            for line in logs:
                self._log.add(line)
            self._after_player_action()

    def _resolve_player_attack(self, action):
        """Called when the player's projectile hits the enemy."""
        enemy_before_hp = self.enemy.hp
        logs = resolve_action(self.player, self.enemy, action)
        for line in logs:
            self._log.add(line)

        # play enemy damage animation if HP decreased
        if self.enemy.hp < enemy_before_hp:
            try:
                self.enemy.play("damage")
            except Exception:
                pass

        self._after_player_action()

    def _after_player_action(self):
        """After player action resolves, check win or schedule enemy turn."""
        if not self.enemy.is_alive():
            self._end_battle("win")
            return

        # Enemy turn after a short delay
        self._turn       = "enemy"
        self._waiting    = True
        self._wait_timer = 0.0

    # ------------------------------------------------------------------
    def _enemy_act(self):
        # Tick down enemy cooldowns
        if self.enemy.special_cooldown > 0:
            self.enemy.special_cooldown -= 1
        action = choose_action(self.enemy, self.player)
        # play enemy animation for this action
        if action == "special" and "special" in self.enemy.animator.animations:
            anim_name = "special"
        else:
            anim_name = {"shoot": "shoot", "cover": "cover", "special": "shoot", "medkit": "medkit"}.get(action, "idle")
        try:
            self.enemy.play(anim_name)
        except Exception:
            pass

        if action in ("shoot", "special"):
            if action == "special":
                self.game.play_special_sfx()
            else:
                self.game.play_bullet_sfx()
            bullet_frames = (self.enemy.special_bullet_frames
                             if action == "special"
                             else self.enemy.bullet_frames)
            # Projectile flies from enemy to player
            start = (self._enemy_pos[0] - 40, self._enemy_pos[1] - 80)
            end = (self._player_pos[0] + 40, self._player_pos[1] - 80)

            def on_hit(act=action):
                self._resolve_enemy_attack(act)

            proj = Projectile(bullet_frames, start, end, duration=0.35, on_hit=on_hit)
            self._projectiles.append(proj)
            self._turn = "projectile_enemy"
        else:
            logs = resolve_action(self.enemy, self.player, action)
            for line in logs:
                self._log.add(line)
            self._after_enemy_action()

    def _resolve_enemy_attack(self, action):
        """Called when the enemy's projectile hits the player."""
        player_before_hp = self.player.hp
        logs = resolve_action(self.enemy, self.player, action)
        for line in logs:
            self._log.add(line)

        if self.player.hp < player_before_hp:
            try:
                self.player.play("damage")
            except Exception:
                pass

        self._after_enemy_action()

    def _after_enemy_action(self):
        """After enemy action resolves, check loss or return to player turn."""
        if not self.player.is_alive():
            if self._try_final_stand_transformation():
                self._turn = "transform"
                return
            self._end_battle("lose")
            return

        self._turn = "player"
        # Tick down cooldowns at start of player turn
        if self.player.special_cooldown > 0:
            self.player.special_cooldown -= 1
        self._update_disabled_buttons()
        # If current selection is now disabled, move to a valid one
        if self._buttons[self._selected].disabled:
            self._skip_to_valid(1)
        self._update_selection()

    def _try_final_stand_transformation(self):
        """Allow one comeback only when the player dies against a final boss."""
        is_final_boss = getattr(self.enemy, '_is_final_boss', False)
        if self._final_stand_used or not is_final_boss:
            return False

        if not hasattr(self.player, "activate_final_boss_form"):
            return False

        # Don't transform immediately; start the warning phase
        self._final_stand_used = True
        self._final_stand_warning_active = True
        self._final_stand_warning_timer = 0.0
        return True

    # ------------------------------------------------------------------
    def _end_battle(self, outcome):
        self._turn = "dying"
        self._death_outcome = outcome
        self._death_timer = 0.0
        self._death_duration = 1.5  # seconds for red tint + fade out
        # Switch the dead character to idle
        dead = self.enemy if outcome == "win" else self.player
        try:
            dead.play("idle")
        except Exception:
            pass

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

        # Update active projectiles
        for proj in self._projectiles:
            proj.update(dt)
        self._projectiles = [p for p in self._projectiles if not p.finished]

        if self._final_stand_warning_active:
            self._final_stand_warning_timer += dt
            if self._final_stand_warning_timer >= self._final_stand_warning_duration:
                self._final_stand_warning_active = False
                self._begin_final_stand_transformation()
            return

        if self._transform_anim_active:
            self._transform_anim_timer += dt
            if self._transform_anim_timer >= self._transform_anim_duration:
                self._transform_anim_active = False
                self._turn = "player"
                self._update_disabled_buttons()
                if self._buttons[self._selected].disabled:
                    self._skip_to_valid(1)
                self._update_selection()
            return

        if self._turn == "dying":
            self._death_timer += dt
            if self._death_timer >= self._death_duration:
                from states.result_state import ResultState
                is_boss = getattr(self.enemy, '_is_boss', False)
                is_final_boss = getattr(self.enemy, '_is_final_boss', False)
                self.game.state_manager.change(
                    ResultState(
                        self.game,
                        self._death_outcome,
                        self.enemy.profile,
                        is_boss=is_boss,
                        is_final_boss=is_final_boss,
                    )
                )
            return

        # When projectile phase is done (all projectiles finished), the on_hit
        # callback already moved the turn forward, so nothing extra needed here.

        if self._waiting:
            self._wait_timer += dt
            if self._wait_timer >= 0.80:
                self._waiting = False
                self._enemy_act()

    # ------------------------------------------------------------------
    def _get_death_alpha(self):
        """Return (is_dying, alpha 0-255) for the dead character during death phase."""
        if self._turn != "dying":
            return False, 255
        progress = min(1.0, self._death_timer / self._death_duration)
        alpha = max(0, int(255 * (1.0 - progress)))
        return True, alpha

    def _begin_final_stand_transformation(self):
        """Actually activate the transformation after warning phase ends."""
        activated = False
        try:
            activated = self.player.activate_final_boss_form()
        except Exception:
            activated = False

        if not activated:
            self._end_battle("lose")
            return

        self._transform_anim_active = True
        self._transform_anim_timer = 0.0
        try:
            self.game.play_special_sfx()
        except Exception:
            pass
        self._log.add("DESPERTAR FINAL: voce assumiu a FORMA BOSS!")

    def _tint_red_and_fade(self, img, alpha):
        """Return a copy of img tinted red with given alpha."""
        tinted = img.copy()
        red_overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        red_overlay.fill((255, 0, 0, 100))
        tinted.blit(red_overlay, (0, 0))
        tinted.set_alpha(alpha)
        return tinted

    def _tint_transform_color(self, img, progress):
        """Apply golden→white→normal tint to sprite during transformation."""
        tinted = img.copy()
        
        if progress < 0.35:
            ratio = progress / 0.35
            r = int(255)
            g = int(200 + 55 * ratio)
            b = int(0 + 55 * ratio)
            alpha = int(140 + 80 * ratio)
        elif progress < 0.7:
            ratio = (progress - 0.35) / 0.35
            r = int(255)
            g = int(255)
            b = int(55 + 200 * ratio)
            alpha = int(220 - 60 * ratio)
        else:
            ratio = (progress - 0.7) / 0.3
            r = int(255 - 60 * ratio)
            g = int(255 - 100 * ratio)
            b = int(255 - 180 * ratio)
            alpha = int(160 * (1.0 - ratio))
        
        color_overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        color_overlay.fill((r, g, b, alpha))
        tinted.blit(color_overlay, (0, 0))
        return tinted

    def _draw_final_stand_warning(self, screen):
        """Draw screen flashing effect with 'ainda não é o fim' message."""
        if not self._final_stand_warning_active:
            return

        progress = min(1.0, self._final_stand_warning_timer / self._final_stand_warning_duration)
        
        # Intense blinking effect (faster pulses)
        blink_cycle = (self._final_stand_warning_timer * 8) % 1.0
        flash_visible = blink_cycle < 0.5
        
        if flash_visible:
            flash = pygame.Surface((W, H), pygame.SRCALPHA)
            flash_alpha = int(220 * (0.5 + progress * 0.5))
            flash.fill((255, 50, 50, flash_alpha))
            screen.blit(flash, (0, 0))
        
        # Message appears mid-way through the warning phase
        if progress > 0.25:
            msg_alpha = int(255 * min(1.0, (progress - 0.25) / 0.25))
            font = pygame.font.SysFont("Courier New", 36, bold=True)
            txt = font.render("AINDA NAO E O FIM", True, (255, 100, 100))
            txt_shadow = font.render("AINDA NAO E O FIM", True, (80, 20, 20))
            
            cx = W // 2 - txt.get_width() // 2
            cy = H // 2 - txt.get_height() // 2
            
            txt_shadow.set_alpha(msg_alpha)
            txt.set_alpha(msg_alpha)
            screen.blit(txt_shadow, (cx + 3, cy + 3))
            screen.blit(txt, (cx, cy))

    def _draw_transformation_overlay(self, screen):
        """Draw transformation animation: golden→white tint on player sprite."""
        if not self._transform_anim_active:
            return

        progress = min(1.0, self._transform_anim_timer / self._transform_anim_duration)

        try:
            px = 80
            py = H - 10
            img = self.player.animator.get_image()
            if img:
                tinted = self._tint_transform_color(img, progress)
                rect = tinted.get_rect(midbottom=(px, py))
                screen.blit(tinted, rect)
        except Exception:
            pass

        if 0.2 < progress < 0.85:
            font = pygame.font.SysFont("Courier New", 28, bold=True)
            txt = font.render("TRANSFORMACAO", True, (255, 255, 255))
            txt_shadow = font.render("TRANSFORMACAO", True, (120, 10, 10))
            cx = W // 2 - txt.get_width() // 2
            cy = 36
            screen.blit(txt_shadow, (cx + 2, cy + 2))
            screen.blit(txt, (cx, cy))

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

        # Death effect state
        is_dying, death_alpha = self._get_death_alpha()
        player_dying = is_dying and getattr(self, '_death_outcome', '') == "lose"
        enemy_dying  = is_dying and getattr(self, '_death_outcome', '') == "win"

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

            # Skip normal draw if transformation animation is active (will draw transformed version)
            if not self._transform_anim_active:
                # draw sprite (uses midbottom anchoring)
                if img is not None and player_dying:
                    tinted = self._tint_red_and_fade(img, death_alpha)
                    rect = tinted.get_rect(midbottom=(px, py))
                    screen.blit(tinted, rect)
                else:
                    self.player.draw(screen, (px, py))

            # draw name + level above sprite
            if img is not None:
                rect = img.get_rect(midbottom=(px, py))
                name_font = pygame.font.SysFont("Courier New", 14, bold=True)
                lvl = getattr(self.player, 'level', 1)
                label = f"{self.player.name}  Lv.{lvl}"
                name_surf = name_font.render(label, True, (50, 200, 80))
                name_r = name_surf.get_rect(midbottom=(rect.centerx, rect.top - 6))
                screen.blit(name_surf, name_r)
        except Exception:
            pass

        # Place HP bars: PLAYER on the left, ENEMY on the right
        try:
            self._player_hp_bar.max_value = max(1, self.player.max_hp)
            self._player_hp_bar.rect.topleft = (ENEMY_BAR_X, ENEMY_BAR_Y)
            self._player_hp_bar.draw(screen, font_small, self.player.hp)
        except Exception:
            pass

        try:
            self._enemy_hp_bar.max_value = max(1, self.enemy.max_hp)
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
                img = None
                try:
                    img = self.enemy.animator.get_image()
                except Exception:
                    img = None

                if img is not None and enemy_dying:
                    tinted = self._tint_red_and_fade(img, death_alpha)
                    rect = tinted.get_rect(midbottom=(ex, ey))
                    screen.blit(tinted, rect)
                else:
                    self.enemy.draw(screen, (ex, ey))

                # draw enemy name above sprite
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

        # Draw projectiles
        for proj in self._projectiles:
            proj.draw(screen)

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

        self._draw_final_stand_warning(screen)
        self._draw_transformation_overlay(screen)
