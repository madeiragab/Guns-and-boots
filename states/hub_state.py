import pygame
from states.base_state import BaseState
from ui.button import Button

WHITE = (255, 255, 255)
GRAY  = (100, 100, 100)
BLACK = (0,   0,   0)

MENU_ITEMS = ["BATALHA", "TROCAR PERSONAGEM", "SAIR"]
MANDATORY_BOSSES = ["Pablo"]


class HubState(BaseState):
    """
    HUB_MENU screen.
    Player chooses what to do next (start a battle, quit…).
    ↑ ↓ navigate, ENTER confirm, ESC → title.
    """

    def on_enter(self):
        self._selected = 0
        W, H = 640, 360
        btn_w, btn_h = 200, 34
        bx = W // 2 - btn_w // 2
        by = H // 2 - (len(MENU_ITEMS) * (btn_h + 8)) // 2
        self._buttons = [
            Button(bx, by + i * (btn_h + 8), btn_w, btn_h, label)
            for i, label in enumerate(MENU_ITEMS)
        ]
        self._update_selection()

    def _update_selection(self):
        for i, btn in enumerate(self._buttons):
            btn.active = (i == self._selected)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self._selected = (self._selected - 1) % len(MENU_ITEMS)
                    self._update_selection()
                elif event.key == pygame.K_DOWN:
                    self._selected = (self._selected + 1) % len(MENU_ITEMS)
                    self._update_selection()
                elif event.key == pygame.K_RETURN:
                    self._confirm()
                elif event.key == pygame.K_ESCAPE:
                    from states.title_state import TitleState
                    self.game.state_manager.change(TitleState(self.game))

    def _confirm(self):
        choice = MENU_ITEMS[self._selected]
        if choice == "BATALHA":
            import random
            import os
            from states.battle_state import BattleState

            if getattr(self.game, 'completed', False):
                # Modo livre: luta aleatoria contra qualquer chefe
                from entities.boss import Boss
                from entities.final_boss import FinalBoss
                boss_base = os.path.join("assets", "sprites", "Bosses")
                final_boss_base = os.path.join("assets", "sprites", "Final Bosses")
                all_bosses = []
                all_final_bosses = []
                try:
                    all_bosses = [f for f in os.listdir(boss_base)
                                  if os.path.isdir(os.path.join(boss_base, f))]
                except Exception:
                    pass

                try:
                    all_final_bosses = [f for f in os.listdir(final_boss_base)
                                        if os.path.isdir(os.path.join(final_boss_base, f))]
                except Exception:
                    pass

                for name in MANDATORY_BOSSES:
                    if name not in all_bosses:
                        all_bosses.append(name)

                if "Paulo" not in all_final_bosses:
                    all_final_bosses.append("Paulo")

                candidates = [("boss", name) for name in all_bosses] + [
                    ("final", name) for name in all_final_bosses
                ]

                if candidates:
                    kind, folder = random.choice(candidates)
                    if kind == "final":
                        boss = FinalBoss(folder, self.game.player)
                    else:
                        boss = Boss(folder)
                    self.game.player.reset_for_battle()
                    self.game.state_manager.change(BattleState(self.game, self.game.player, boss))
                return

            from entities.enemy import Enemy
            # Fresh run — reset enemy progression and player level
            self.game.defeated_enemies = []
            self.game.enemy_round = 0
            self.game.player.level = 1
            self.game.player.atk = 7
            self.game.player.max_hp = 30
            self.game.player.hp = 30

            # Look for available enemy folders under assets/sprites/Enemy
            base = os.path.join("assets", "sprites", "Enemy")
            enemy_folders = []
            try:
                for name in os.listdir(base):
                    full = os.path.join(base, name)
                    if os.path.isdir(full):
                        enemy_folders.append(name)
            except Exception:
                enemy_folders = []

            if enemy_folders:
                profile = random.choice(enemy_folders)
                print(f"[HubState] starting fresh run -> chosen: {profile}")
            else:
                profile = random.choice(["GRUNT", "HEAVY", "SNIPER"])
                print(f"[HubState] no enemy folders, chosen profile: {profile}")

            enemy = Enemy(profile)
            self.game.player.reset_for_battle()
            self.game.state_manager.change(BattleState(self.game, self.game.player, enemy))
        elif choice == "TROCAR PERSONAGEM":
            from states.select_state import SelectState
            name = getattr(self.game, 'player_name', None) or getattr(self.game.player, 'name', 'JOGADOR')
            self.game.state_manager.change(SelectState(self.game, name))
        elif choice == "SAIR":
            self.game.quit()

    def update(self, dt):
        pass

    def draw(self, screen):
        W, H = screen.get_size()
        font_title = pygame.font.SysFont("Courier New", 26, bold=True)
        font_small = pygame.font.SysFont("Courier New", 13)
        font_btn   = pygame.font.SysFont("Courier New", 16)

        # Heading
        welcome = font_title.render(
            f"BEM-VINDO, {self.game.player.name}", True, WHITE
        )
        screen.blit(welcome, (W // 2 - welcome.get_width() // 2, 60))

        sub_txt = ("MODO LIVRE — enfrente qualquer chefe!"
                   if getattr(self.game, 'completed', False)
                   else "Escolha sua proxima acao.")
        sub = font_small.render(sub_txt, True, GRAY)
        screen.blit(sub, (W // 2 - sub.get_width() // 2, 100))

        # Buttons
        for btn in self._buttons:
            btn.draw(screen, font_btn)

        # Hint
        hint = font_small.render("↑↓ navigate    ENTER select    ESC title", True, GRAY)
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 30))
