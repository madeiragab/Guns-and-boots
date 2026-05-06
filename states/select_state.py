import os
import pygame
from states.base_state import BaseState
from core.sprite_animator import load_animations_from_folders, SpriteAnimator
from ui.font_cache import get_font
from core.paths import get_asset_path

WHITE  = (255, 255, 255)
GRAY   = (100, 100, 100)
DARK   = (40,  40,  50)
BLACK  = (0,   0,   0)
YELLOW = (180, 180, 60)
RED    = (200, 40,  40)
GREEN  = (50,  200, 80)

PLAYERS_BASE = get_asset_path("sprites", "Players")
PREVIEW_SIZE = (128, 128)

W, H = 640, 360


class SelectState(BaseState):
    """
    CHARACTER SELECT — carousel style.
    ← → to browse characters, ENTER to confirm (unlocked only), ESC back.
    """

    def __init__(self, game, player_name):
        super().__init__(game)
        self.player_name = player_name

    def on_enter(self):
        self._selected = 0
        self._characters = []
        self._box_rect = None
        self._left_arrow_rect = None
        self._right_arrow_rect = None

        try:
            folders = sorted(
                f for f in os.listdir(PLAYERS_BASE)
                if os.path.isdir(os.path.join(PLAYERS_BASE, f))
            )
        except Exception:
            folders = []

        unlocked = getattr(self.game, 'unlocked_players', ["Pablo"])

        for folder in folders:
            path = os.path.join(PLAYERS_BASE, folder)
            try:
                anims = load_animations_from_folders(
                    path, scale=1, colorkey=(0, 0, 0), target_size=PREVIEW_SIZE
                )
            except Exception:
                anims = {}

            if not anims:
                s = pygame.Surface(PREVIEW_SIZE, pygame.SRCALPHA)
                s.fill((100, 100, 100, 255))
                anims = {"idle": [s]}

            animator = SpriteAnimator(anims, default="idle", fps=10, return_to_idle=True)
            animator.play("idle", loop=True, reset=True)

            self._characters.append({
                "folder": folder,
                "name": folder,
                "animator": animator,
                "unlocked": folder in unlocked,
            })

        # Inicia a selecao no primeiro personagem desbloqueado
        for i, ch in enumerate(self._characters):
            if ch["unlocked"]:
                self._selected = i
                break

    # ------------------------------------------------------------------
    def handle_events(self, events):
        if not self._characters:
            return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_UP):
                    self._selected = (self._selected - 1) % len(self._characters)
                elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                    self._selected = (self._selected + 1) % len(self._characters)
                elif event.key == pygame.K_RETURN:
                    ch = self._characters[self._selected]
                    if ch["unlocked"]:
                        self._confirm()
                elif event.key == pygame.K_ESCAPE:
                    from states.name_state import NameInputState
                    self.game.state_manager.change(NameInputState(self.game))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # allow tapping the box to confirm or arrows to change
                mobile = getattr(self.game, 'mobile', False)
                pt = event.pos
                if self._box_rect and self._box_rect.collidepoint(pt):
                    ch = self._characters[self._selected]
                    if ch["unlocked"]:
                        self._confirm()
                        return
                if self._left_arrow_rect and self._left_arrow_rect.collidepoint(pt):
                    self._selected = (self._selected - 1) % len(self._characters)
                    return
                if self._right_arrow_rect and self._right_arrow_rect.collidepoint(pt):
                    self._selected = (self._selected + 1) % len(self._characters)
                    return

    # ------------------------------------------------------------------
    def _confirm(self):
        chosen = self._characters[self._selected]
        from entities.player import Player
        from states.hub_state import HubState
        self.game.player_name = self.player_name
        self.game.player = Player(self.player_name, folder=chosen["folder"])
        self.game.save_game()
        self.game.state_manager.change(HubState(self.game))

    # ------------------------------------------------------------------
    def update(self, dt):
        for ch in self._characters:
            ch["animator"].update(dt)

    # ------------------------------------------------------------------
    def draw(self, screen):
        screen.fill(BLACK)

        font_title = get_font("Courier New", 22, bold=True)
        font_name  = get_font("Courier New", 16, bold=True)
        font_info  = get_font("Courier New", 13)
        font_hint  = get_font("Courier New", 12)
        font_lock  = get_font("Courier New", 36, bold=True)
        font_arrow = get_font("Courier New", 36, bold=True)

        # Titulo
        title = font_title.render("ESCOLHA SEU PERSONAGEM", True, WHITE)
        screen.blit(title, (W // 2 - title.get_width() // 2, 24))

        if not self._characters:
            msg = font_name.render("Nenhum personagem encontrado.", True, GRAY)
            screen.blit(msg, (W // 2 - msg.get_width() // 2, H // 2))
            return

        ch = self._characters[self._selected]

        # ── Caixa central de visualizacao ────────────────────────────
        box_w = PREVIEW_SIZE[0] + 32
        box_h = PREVIEW_SIZE[1] + 32
        box_x = W // 2 - box_w // 2
        box_y = H // 2 - box_h // 2 - 20

        bg_color = DARK if ch["unlocked"] else (20, 20, 25)
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(screen, bg_color, box_rect)

        border_color = YELLOW if ch["unlocked"] else (60, 30, 30)
        border_w = 3 if ch["unlocked"] else 2
        pygame.draw.rect(screen, border_color, box_rect, border_w)

        # Pre-visualizacao do sprite
        img = ch["animator"].get_image()
        if img:
            dx = box_x + (box_w - img.get_width()) // 2
            dy = box_y + (box_h - img.get_height()) // 2

            if ch["unlocked"]:
                screen.blit(img, (dx, dy))
            else:
                # Versao escurecida
                dimmed = img.copy()
                dark_overlay = pygame.Surface(dimmed.get_size(), pygame.SRCALPHA)
                dark_overlay.fill((0, 0, 0, 160))
                dimmed.blit(dark_overlay, (0, 0))
                screen.blit(dimmed, (dx, dy))

                # X vermelha sobre personagem bloqueado
                x_text = font_lock.render("X", True, RED)
                screen.blit(x_text, (
                    box_x + box_w // 2 - x_text.get_width() // 2,
                    box_y + box_h // 2 - x_text.get_height() // 2
                ))

        # ── Setas de navegacao ───────────────────────────────────────
        if len(self._characters) > 1:
            arr_l = font_arrow.render("<", True, WHITE)
            arr_r = font_arrow.render(">", True, WHITE)
            lx = box_x - 50
            ly = box_y + box_h // 2 - arr_l.get_height() // 2
            rx = box_x + box_w + 20
            ry = box_y + box_h // 2 - arr_r.get_height() // 2
            screen.blit(arr_l, (lx, ly))
            screen.blit(arr_r, (rx, ry))
            # store hit rects for touch handling
            self._left_arrow_rect = pygame.Rect(lx, ly, arr_l.get_width(), arr_l.get_height())
            self._right_arrow_rect = pygame.Rect(rx, ry, arr_r.get_width(), arr_r.get_height())

        # ── Nome do personagem ───────────────────────────────────────
        name_color = WHITE if ch["unlocked"] else GRAY
        name_surf = font_name.render(ch["name"], True, name_color)
        screen.blit(name_surf, (W // 2 - name_surf.get_width() // 2, box_y + box_h + 10))

        # Contador (ex.: "2 / 5")
        counter = font_info.render(
            f"{self._selected + 1} / {len(self._characters)}", True, GRAY
        )
        screen.blit(counter, (W // 2 - counter.get_width() // 2, box_y + box_h + 30))

        # Status de bloqueio
        if ch["unlocked"]:
            status = font_info.render("DESBLOQUEADO", True, GREEN)
        else:
            status = font_info.render("BLOQUEADO", True, RED)
        screen.blit(status, (W // 2 - status.get_width() // 2, box_y + box_h + 48))

        # store box rect for touch handling
        self._box_rect = box_rect

        # ── Dicas ────────────────────────────────────────────────────
        hint = font_hint.render(
            "\u2190 \u2192 mudar     ENTER selecionar     ESC voltar", True, GRAY
        )
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 24))
