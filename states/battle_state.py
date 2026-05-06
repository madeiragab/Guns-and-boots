import pygame
from states.base_state import BaseState
from ui.button    import Button
from ui.healthbar import HealthBar
from ui.logbox    import LogBox
from systems.combat import resolve_action
from systems.ai     import choose_action
from entities.projectile import Projectile
from ui.font_cache import get_font
from core.paths import get_asset_path
import os
import random

WHITE  = (255, 255, 255)
GRAY   = (80,  80,  80)
BLACK  = (0,   0,   0)
RED    = (200, 40,  40)
ORANGE = (210, 130, 0)

ACTIONS = ["ATIRAR", "COBERTURA", "ESPECIAL", "MEDKIT"]

# ── Constantes de layout ──────────────────────────────────────────────
W, H = 640, 360

# Paineis
PANEL_W       = W // 2 - 10
ENEMY_PANEL_H = 68
PLAYER_PANEL_H = 90

# Painel do inimigo (superior esquerdo)
ENEMY_PANEL_Y = 0
ENEMY_BAR_X   = 12
ENEMY_BAR_Y   = ENEMY_PANEL_Y + 34    # abaixo do rotulo de nome
ENEMY_BAR_W   = 260
ENEMY_BAR_H   = 16

# Painel do jogador (inferior esquerdo)
PLAYER_PANEL_Y = H - PLAYER_PANEL_H
PLAYER_BAR_X   = 12
PLAYER_BAR_Y   = PLAYER_PANEL_Y + 30
PLAYER_BAR_W   = 260
PLAYER_BAR_H   = 16
HEAT_BAR_Y     = PLAYER_PANEL_Y + 64
HEAT_BAR_W     = 180
HEAT_BAR_H     = 10

# Menu de acoes (inferior direito) -- mantido para o layout de entrada, embora nao seja desenhado
MENU_X     = W // 2 + 20
MENU_Y     = H - 130
BTN_W, BTN_H = 170, 22
BTN_GAP    = 4

# Caixa de log (nao desenhada atualmente)
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
        self._projectiles = []  # projetis ativos na tela

        # Posicoes dos sprites (usadas para inicio/fim dos projetis)
        self._player_pos = (80, H - 10)
        self._enemy_pos = (W - 80, H - 10)

        # Botoes (mantidos para tratar entrada, mas nao desenhados)
        self._buttons = [
            Button(MENU_X, MENU_Y + i * (BTN_H + BTN_GAP), BTN_W, BTN_H, label)
            for i, label in enumerate(ACTIONS)
        ]
        self._update_disabled_buttons()
        self._update_selection()

        # Barras de vida de cada combatente; ficam posicionadas acima dos sprites
        bar_w, bar_h = 120, 12
        self._enemy_hp_bar = HealthBar(0, 0, bar_w, bar_h, self.enemy.max_hp, label="HP INIMIGO", dynamic_color=True)
        self._player_hp_bar = HealthBar(0, 0, bar_w, bar_h, self.player.max_hp, label="HP JOGADOR", dynamic_color=True)

        # Log mantido, mas nao desenhado
        self._log = LogBox(LOG_X, LOG_Y, LOG_W, LOG_H, max_lines=5)
        self._log.add("Batalha iniciada!")

        try:
            self.player.play("idle")
        except Exception:
            pass

        # Escolhe um fundo de campo aleatorio em assets/sprites/field (busca recursiva)
        try:
            base_field = get_asset_path("sprites", "field")
            choices = []
            for root, dirs, files in os.walk(base_field):
                for fn in files:
                    if fn.lower().endswith((".png", ".jpg", ".jpeg")):
                        choices.append(os.path.join(root, fn))

            if choices:
                pick = random.choice(choices)
                # Evita convert_alpha/convert aqui caso o display ainda nao esteja totalmente inicializado;
                # pygame.image.load sozinho retorna uma Surface utilizavel.
                surf = pygame.image.load(pick)
                # escala para preencher a tela preservando a proporcao
                sw, sh = surf.get_size()
                scale = max(W / sw, H / sh)
                nw, nh = int(sw * scale), int(sh * scale)
                surf = pygame.transform.smoothscale(surf, (nw, nh))
                # recorte central para a janela
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
        # Reserva com tudo desabilitado (nao deveria acontecer)
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # allow tapping the on-screen action buttons
                mobile = getattr(self.game, 'mobile', False)
                for i, btn in enumerate(self._buttons):
                    if btn.handle_event(event, mobile=mobile):
                        if not btn.disabled:
                            self._selected = i
                            self._update_selection()
                            self._player_act(ACTIONS[self._selected].lower().replace(" ", "_"))
                        break

    # ------------------------------------------------------------------
    def _player_act(self, action):
        action = action.replace("atirar", "shoot").replace("cobertura", "cover").replace("especial", "special")
        # toca a animacao correspondente
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

        # Para tiro/especial, cria um projetil primeiro e resolve no acerto
        if action in ("shoot", "special"):
            if action == "special":
                self.game.play_special_sfx()
            else:
                self.game.play_bullet_sfx()
            bullet_frames = (self.player.special_bullet_frames
                             if action == "special"
                             else self.player.bullet_frames)
            # O projetil voa do jogador para o inimigo
            start = (self._player_pos[0] + 40, self._player_pos[1] - 80)
            end = (self._enemy_pos[0] - 40, self._enemy_pos[1] - 80)

            def on_hit():
                self._resolve_player_attack(action)

            proj = Projectile(bullet_frames, start, end, duration=0.35, on_hit=on_hit)
            self._projectiles.append(proj)
            self._turn = "projectile"
        else:
            # Acoes sem projetil resolvem imediatamente
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

        # toca animacao de dano do inimigo se o HP diminuir
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

        # Turno do inimigo apos um pequeno atraso
        self._turn       = "enemy"
        self._waiting    = True
        self._wait_timer = 0.0

    # ------------------------------------------------------------------
    def _enemy_act(self):
        # Reduz os cooldowns do inimigo
        if self.enemy.special_cooldown > 0:
            self.enemy.special_cooldown -= 1
        action = choose_action(self.enemy, self.player)
        # toca a animacao do inimigo para esta acao
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
            # O projetil voa do inimigo para o jogador
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
        # Reduz cooldowns no inicio do turno do jogador
        if self.player.special_cooldown > 0:
            self.player.special_cooldown -= 1
        self._update_disabled_buttons()
        # Se a selecao atual estiver desabilitada, move para uma opcao valida
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

        # Nao transforma imediatamente; inicia a fase de aviso
        self._final_stand_used = True
        self._final_stand_warning_active = True
        self._final_stand_warning_timer = 0.0
        return True

    # ------------------------------------------------------------------
    def _end_battle(self, outcome):
        self._turn = "dying"
        self._death_outcome = outcome
        self._death_timer = 0.0
        self._death_duration = 1.5  # segundos para tonalidade vermelha + fade out
        # Muda o personagem morto para estado ocioso (idle)
        dead = self.enemy if outcome == "win" else self.player
        try:
            dead.play("idle")
        except Exception:
            pass

    # ------------------------------------------------------------------
    def update(self, dt):
        # atualiza a animacao do jogador
        try:
            self.player.update(dt)
        except Exception:
            pass
        # atualiza a animacao do inimigo
        try:
            self.enemy.update(dt)
        except Exception:
            pass

        # Atualiza os projetis ativos
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

        # Quando a fase de projetis termina (todos concluidos), o on_hit
        # o retorno ja avancou o turno, entao nada extra e necessario aqui.

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
        
        # Efeito de piscada intensa (pulsos mais rapidos)
        blink_cycle = (self._final_stand_warning_timer * 8) % 1.0
        flash_visible = blink_cycle < 0.5
        
        if flash_visible:
            flash = pygame.Surface((W, H), pygame.SRCALPHA)
            flash_alpha = int(220 * (0.5 + progress * 0.5))
            flash.fill((255, 50, 50, flash_alpha))
            screen.blit(flash, (0, 0))
        
        # A mensagem aparece na metade da fase de aviso
        if progress > 0.25:
            msg_alpha = int(255 * min(1.0, (progress - 0.25) / 0.25))
            font = get_font("Courier New", 36, bold=True)
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
            font = get_font("Courier New", 28, bold=True)
            txt = font.render("TRANSFORMACAO", True, (255, 255, 255))
            txt_shadow = font.render("TRANSFORMACAO", True, (120, 10, 10))
            cx = W // 2 - txt.get_width() // 2
            cy = 36
            screen.blit(txt_shadow, (cx + 2, cy + 2))
            screen.blit(txt, (cx, cy))

    # ------------------------------------------------------------------
    def draw(self, screen):
        # Desenha o fundo de campo se disponivel; caso contrario, fundo preto total.
        if getattr(self, "_field_surf", None) is not None:
            try:
                screen.blit(self._field_surf, (0, 0))
            except Exception:
                screen.fill((0, 0, 0))
        else:
            screen.fill((0, 0, 0))

        font_small = get_font("Courier New", 12)

        # Estado do efeito de morte
        is_dying, death_alpha = self._get_death_alpha()
        player_dying = is_dying and getattr(self, '_death_outcome', '') == "lose"
        enemy_dying  = is_dying and getattr(self, '_death_outcome', '') == "win"

        # Opcional: desenha o sprite do jogador na area esquerda (atras de onde a UI ficava)
        try:
            # jogador no canto inferior esquerdo (pes ancorados), movido levemente para a direita
            px = 80
            py = H - 10
            # desenha o sprite e tambem renderiza o nome do jogador acima dele
            img = None
            try:
                img = self.player.animator.get_image()
            except Exception:
                img = None

            # Pula o desenho normal se a animacao de transformacao estiver ativa (desenha a versao transformada)
            if not self._transform_anim_active:
                # desenha o sprite (usa ancoragem midbottom)
                if img is not None and player_dying:
                    tinted = self._tint_red_and_fade(img, death_alpha)
                    rect = tinted.get_rect(midbottom=(px, py))
                    screen.blit(tinted, rect)
                else:
                    self.player.draw(screen, (px, py))

            # desenha nome + nivel acima do sprite
            if img is not None:
                rect = img.get_rect(midbottom=(px, py))
                name_font = get_font("Courier New", 14, bold=True)
                lvl = getattr(self.player, 'level', 1)
                label = f"{self.player.name}  Lv.{lvl}"
                name_surf = name_font.render(label, True, (50, 200, 80))
                name_r = name_surf.get_rect(midbottom=(rect.centerx, rect.top - 6))
                screen.blit(name_surf, name_r)
        except Exception:
            pass

        # Posiciona barras de HP: JOGADOR a esquerda, INIMIGO a direita
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

        # Desenha o sprite do inimigo no canto inferior direito (pes ancorados)
        try:
            ex = W - 80
            ey = H - 10
            # o animador do inimigo e atualizado em update(dt)

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

                # desenha o nome do inimigo acima do sprite
                if img is not None:
                    rect = img.get_rect(midbottom=(ex, ey))
                    name_font = get_font("Courier New", 14, bold=True)
                    lbl = name_font.render(self.enemy.name, True, (200, 40, 40))
                    lbl_r = lbl.get_rect(midbottom=(rect.centerx, rect.top - 6))
                    screen.blit(lbl, lbl_r)
            except Exception:
                # caixa placeholder de reserva
                box_w, box_h = 80, 120
                surf = pygame.Surface((box_w, box_h))
                surf.fill((40, 40, 40))
                rect = surf.get_rect(midbottom=(ex, ey))
                pygame.draw.rect(surf, (80, 80, 80), surf.get_rect(), 2)
                screen.blit(surf, rect)
                name_font = get_font("Courier New", 14, bold=True)
                lbl = name_font.render(self.enemy.name, True, (200, 40, 40))
                lbl_r = lbl.get_rect(midbottom=(rect.centerx, rect.top - 6))
                screen.blit(lbl, lbl_r)
        except Exception:
            pass

        # Desenha projetis
        for proj in self._projectiles:
            proj.draw(screen)

        # Desenha botoes centralizados embaixo (linha compacta)
        try:
            mobile = getattr(self.game, 'mobile', False)
            btn_count = len(self._buttons)
            # Ajusta tamanho e fonte para mobile vs desktop
            if mobile:
                btn_w = max(120, BTN_W)
                btn_h = max(40, BTN_H * 2)
                gap = max(8, BTN_GAP * 2)
                font = get_font("Courier New", 18, bold=True)
            else:
                btn_w = BTN_W
                btn_h = BTN_H
                gap = BTN_GAP
                font = get_font("Courier New", 13)

            total_w = btn_w * btn_count + gap * (btn_count - 1)
            start_x = W // 2 - total_w // 2
            y = H - btn_h - (20 if mobile else 10)
            for i, btn in enumerate(self._buttons):
                bx = start_x + i * (btn_w + gap)
                btn.rect.topleft = (bx, y)
                btn.rect.width = btn_w
                btn.rect.height = btn_h
                btn.draw(screen, font)
        except Exception:
            pass

        self._draw_final_stand_warning(screen)
        self._draw_transformation_overlay(screen)
