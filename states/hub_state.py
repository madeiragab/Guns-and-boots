import pygame
from states.base_state import BaseState
from ui.button import Button

WHITE = (255, 255, 255)
GRAY  = (100, 100, 100)
BLACK = (0,   0,   0)

MENU_ITEMS = ["BATTLE", "QUIT"]


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
        if choice == "BATTLE":
            import random
            import os
            from entities.enemy import Enemy
            from states.battle_state import BattleState

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
                print(f"[HubState] enemy_folders={enemy_folders} -> chosen: {profile}")
            else:
                profile = random.choice(["GRUNT", "HEAVY", "SNIPER"])
                print(f"[HubState] no enemy folders, chosen profile: {profile}")

            enemy = Enemy(profile)
            self.game.player.reset_for_battle()
            self.game.state_manager.change(BattleState(self.game, self.game.player, enemy))
        elif choice == "QUIT":
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
            f"WELCOME, {self.game.player.name}", True, WHITE
        )
        screen.blit(welcome, (W // 2 - welcome.get_width() // 2, 60))

        sub = font_small.render("Choose your next move.", True, GRAY)
        screen.blit(sub, (W // 2 - sub.get_width() // 2, 100))

        # Buttons
        for btn in self._buttons:
            btn.draw(screen, font_btn)

        # Hint
        hint = font_small.render("↑↓ navigate    ENTER select    ESC title", True, GRAY)
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 30))
