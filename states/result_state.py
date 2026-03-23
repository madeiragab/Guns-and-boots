import os
import random

import pygame
from states.base_state import BaseState

WHITE  = (255, 255, 255)
GRAY   = (100, 100, 100)
GREEN  = (50,  200, 80)
RED    = (200, 40,  40)
YELLOW = (255, 220, 50)
MANDATORY_BOSSES = ["Pablo"]


class ResultState(BaseState):
    """
    RESULT screen.
    Shows WIN or LOSE.
    On win: levels up the player and advances to the next battle.
    On lose: returns to the hub.
    """

    def __init__(self, game, outcome, enemy_profile=None, is_boss=False, is_final_boss=False):
        super().__init__(game)
        self.outcome = outcome          # "vitoria" | "derrota"
        self.enemy_profile = enemy_profile
        self.is_boss = is_boss
        self.is_final_boss = is_final_boss
        self._all_cleared = False
        self._boss_victory = False
        self._final_boss_victory = False
        self._all_bosses_cleared = False
        self._all_final_bosses_cleared = False

    def on_enter(self):
        self._blink_timer   = 0.0
        self._blink_visible = True
        self._fade_in_timer = 0.0
        self._fade_in_duration = 1.0  # segundos para aparecer gradualmente
        self._accept_input = False

        # A transformacao de ultima resistencia e temporaria e nao deve vazar para outras batalhas.
        try:
            if getattr(self.game.player, "_in_boss_form", False):
                self.game.player.revert_from_boss_form()
        except Exception:
            pass

        if self.outcome == "win":
            if self.is_final_boss:
                if self.enemy_profile and self.enemy_profile not in self.game.defeated_final_bosses:
                    self.game.defeated_final_bosses.append(self.enemy_profile)
                self._all_final_bosses_cleared = not self._get_undefeated_final_bosses()
                self.game.save_game()
                self._final_boss_victory = True
            elif self.is_boss:
                # Desbloqueia o personagem jogavel correspondente
                if self.enemy_profile and self.enemy_profile not in self.game.unlocked_players:
                    self.game.unlocked_players.append(self.enemy_profile)
                if self.enemy_profile and self.enemy_profile not in self.game.defeated_bosses:
                    self.game.defeated_bosses.append(self.enemy_profile)
                self._all_bosses_cleared = not self._get_undefeated_bosses()
                self.game.save_game()
                self._boss_victory = True
            else:
                # Inimigo comum derrotado
                if self.enemy_profile and self.enemy_profile not in self.game.defeated_enemies:
                    self.game.defeated_enemies.append(self.enemy_profile)
                self._all_cleared = not self._get_available_enemies()

    # ------------------------------------------------------------------
    def _get_available_enemies(self):
        base = os.path.join("assets", "sprites", "Enemy")
        folders = []
        try:
            for name in os.listdir(base):
                if os.path.isdir(os.path.join(base, name)):
                    folders.append(name)
        except Exception:
            pass
        return [f for f in folders if f not in self.game.defeated_enemies]

    def _get_undefeated_bosses(self):
        base = os.path.join("assets", "sprites", "Bosses")
        folders = []
        try:
            for name in os.listdir(base):
                if os.path.isdir(os.path.join(base, name)):
                    folders.append(name)
        except Exception:
            pass

        for name in MANDATORY_BOSSES:
            if name not in folders:
                folders.append(name)

        defeated = getattr(self.game, 'defeated_bosses', [])
        return [f for f in folders if f not in defeated]

    def _get_undefeated_final_bosses(self):
        base = os.path.join("assets", "sprites", "Final Bosses")
        folders = []
        try:
            for name in os.listdir(base):
                if os.path.isdir(os.path.join(base, name)):
                    folders.append(name)
        except Exception:
            pass

        if "Paulo" not in folders:
            folders.append("Paulo")

        defeated = getattr(self.game, 'defeated_final_bosses', [])
        return [f for f in folders if f not in defeated]

    def _prepare_final_boss_retry(self):
        """On final-boss defeat, force a new run: 3 enemies + 1 boss before rematch."""
        boss_folders = []
        base = os.path.join("assets", "sprites", "Bosses")
        try:
            for name in os.listdir(base):
                if os.path.isdir(os.path.join(base, name)):
                    boss_folders.append(name)
        except Exception:
            pass

        for name in MANDATORY_BOSSES:
            if name not in boss_folders:
                boss_folders.append(name)

        defeated_now = list(getattr(self.game, "defeated_bosses", []))
        retry_candidates = [name for name in defeated_now if name in boss_folders]
        if not retry_candidates:
            retry_candidates = list(boss_folders)

        retry_boss = random.choice(retry_candidates) if retry_candidates else None
        if retry_boss is not None:
            self.game.defeated_bosses = [name for name in defeated_now if name != retry_boss]

        # Reinicia a progressao dos inimigos para o jogador limpar os inimigos antes do chefe novamente.
        self.game.defeated_enemies = []
        self.game.enemy_round = 0

        # Mantem o modo campanha ativo e lembra qual chefe final deve ser tentado de novo.
        self.game.completed = False
        self.game.final_boss_retry_target = self.enemy_profile
        self.game.save_game()

    # ------------------------------------------------------------------
    def handle_events(self, events):
        if not self._accept_input:
            return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self._final_boss_victory:
                        if self._all_final_bosses_cleared and not getattr(self.game, 'completed', False):
                            self.game.complete_game()
                            from states.credits_state import CreditsState
                            self.game.state_manager.change(CreditsState(self.game))
                        else:
                            from states.hub_state import HubState
                            self.game.state_manager.change(HubState(self.game))
                    elif self._boss_victory:
                        if self._all_bosses_cleared and not getattr(self.game, 'completed', False):
                            from states.final_danger_state import FinalDangerState
                            self.game.state_manager.change(FinalDangerState(self.game))
                        elif not getattr(self.game, 'completed', False):
                            from states.danger_state import DangerState
                            self.game.state_manager.change(DangerState(self.game))
                        else:
                            from states.hub_state import HubState
                            self.game.state_manager.change(HubState(self.game))
                    elif self.outcome == "win" and self._all_cleared:
                        if self._get_undefeated_bosses():
                            self.game.player.level_up()
                            from states.danger_state import DangerState
                            self.game.state_manager.change(DangerState(self.game))
                        else:
                            from states.hub_state import HubState
                            self.game.state_manager.change(HubState(self.game))
                    elif self.outcome == "win":
                        self._advance_to_next_battle()
                    else:
                        if self.is_final_boss and not getattr(self.game, 'completed', False):
                            self._prepare_final_boss_retry()
                        from states.hub_state import HubState
                        self.game.state_manager.change(HubState(self.game))
                elif event.key == pygame.K_SPACE:
                    # "Preparar mais" - repetir todos os inimigos para subir de nivel
                    if self.outcome == "win" and self._all_cleared and self._get_undefeated_bosses():
                        self._restart_enemy_gauntlet()
                elif event.key == pygame.K_ESCAPE:
                    self.game.quit()

    # ------------------------------------------------------------------
    def _advance_to_next_battle(self):
        from entities.enemy import Enemy
        from states.battle_state import BattleState

        self.game.player.level_up()

        available = self._get_available_enemies()
        if not available:
            from states.hub_state import HubState
            self.game.state_manager.change(HubState(self.game))
            return

        profile = random.choice(available)
        enemy = Enemy(profile, level=self.game.enemy_round)
        self.game.player.reset_for_battle()
        self.game.state_manager.change(
            BattleState(self.game, self.game.player, enemy)
        )

    def _restart_enemy_gauntlet(self):
        """Reset defeated enemies list and start fighting them again."""
        from entities.enemy import Enemy
        from states.battle_state import BattleState

        self.game.player.level_up()
        self.game.defeated_enemies = []
        self.game.enemy_round += 1

        available = self._get_available_enemies()
        if not available:
            from states.hub_state import HubState
            self.game.state_manager.change(HubState(self.game))
            return

        profile = random.choice(available)
        enemy = Enemy(profile, level=self.game.enemy_round)
        self.game.player.reset_for_battle()
        self.game.state_manager.change(
            BattleState(self.game, self.game.player, enemy)
        )

    # ------------------------------------------------------------------
    def update(self, dt):
        self._fade_in_timer += dt
        if self._fade_in_timer >= self._fade_in_duration:
            self._accept_input = True

        self._blink_timer += dt
        if self._blink_timer >= 0.55:
            self._blink_timer   = 0.0
            self._blink_visible = not self._blink_visible

    # ------------------------------------------------------------------
    def draw(self, screen):
        W, H = screen.get_size()
        font_big   = pygame.font.SysFont("Courier New", 48, bold=True)
        font_mid   = pygame.font.SysFont("Courier New", 18)
        font_small = pygame.font.SysFont("Courier New", 13)

        fade_progress = min(1.0, self._fade_in_timer / self._fade_in_duration)
        alpha = int(255 * fade_progress)

        content = pygame.Surface((W, H), pygame.SRCALPHA)

        if self.outcome == "win":
            color = GREEN
            if self._final_boss_victory:
                if self._all_final_bosses_cleared and not getattr(self.game, 'completed', False):
                    text = "VITORIA FINAL"
                    flavour = "PAULO CAIU. O FIM CHEGOU."
                    prompt_txt = "ENTER \u2192 creditos     ESC \u2192 sair"
                else:
                    text = "BOSS FINAL DERROTADO"
                    flavour = f"{self.enemy_profile} derrotado!"
                    prompt_txt = "ENTER \u2192 menu     ESC \u2192 sair"
            elif self._boss_victory:
                if self._all_bosses_cleared and not getattr(self.game, 'completed', False):
                    text = "ULTIMO CHEFE LIMPO"
                    flavour = "A ameaca final apareceu..."
                    prompt_txt = "ENTER \u2192 boss final     ESC \u2192 sair"
                else:
                    text = "CHEFE DERROTADO"
                    flavour = (f"{self.enemy_profile} DERROTADO!"
                               if getattr(self.game, 'completed', False)
                               else f"{self.enemy_profile} DESBLOQUEADO!")
                    if getattr(self.game, 'completed', False):
                        prompt_txt = "ENTER \u2192 menu     ESC \u2192 sair"
                    else:
                        prompt_txt = "ENTER \u2192 proximo chefe     ESC \u2192 sair"
            elif self._all_cleared:
                if self._get_undefeated_bosses():
                    text = "TUDO LIMPO"
                    flavour = "Prepare-se para enfrentar o CHEFE..."
                    prompt_txt = "ENTER \u2192 chefe     SPACE \u2192 se preparar mais     ESC \u2192 sair"
                else:
                    text = "VITORIA"
                    flavour = "Todos os inimigos e chefes derrotados!"
                    prompt_txt = "ENTER \u2192 menu     ESC \u2192 sair"
            else:
                lvl = self.game.player.level
                flavour = f"Nivel {lvl} \u2192 {lvl + 1}   (+1 ATK, +10 HP)"
                text = "VITORIA"
                prompt_txt = "ENTER \u2192 proxima batalha     ESC \u2192 sair"
        else:
            color   = RED
            text    = "DERROTADO"
            flavour = "Voce foi eliminado."
            prompt_txt = "ENTER \u2192 menu     ESC \u2192 sair"

        result = font_big.render(text, True, color)
        content.blit(result, (W // 2 - result.get_width() // 2, H // 3 - 20))

        flav = font_mid.render(flavour, True, WHITE)
        content.blit(flav, (W // 2 - flav.get_width() // 2, H // 3 + 60))

        if self._accept_input and self._blink_visible:
            prompt = font_small.render(prompt_txt, True, GRAY)
            content.blit(prompt, (W // 2 - prompt.get_width() // 2, H * 2 // 3))

        content.set_alpha(alpha)
        screen.blit(content, (0, 0))
