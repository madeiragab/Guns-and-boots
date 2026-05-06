import pygame
from states.base_state import BaseState
from ui.font_cache import get_font

WHITE = (255, 255, 255)
GRAY  = (100, 100, 100)
RED   = (200, 40,  40)
BLACK = (0,   0,   0)

MAX_NAME_LEN = 12


class NameInputState(BaseState):
    """
    NAME_INPUT screen.
    Player types a name, confirms with ENTER.
    ESC returns to title.
    """

    def on_enter(self):
        self._name          = ""
        self._error         = ""
        self._blink_timer   = 0.0
        self._cursor_on     = True
        self._ok_rect = None
        self._del_rect = None
        self._text_input_active = False
        # On mobile, request the system soft-keyboard (SDL2/pygame support)
        try:
            if getattr(self.game, 'mobile', False):
                pygame.key.start_text_input()
                self._text_input_active = True
        except Exception:
            self._text_input_active = False

    def handle_events(self, events):
        for event in events:
            # Text input events (recommended on SDL2/mobile)
            if event.type == pygame.TEXTINPUT:
                txt = event.text
                # Accept letters, space, dash, underscore
                for ch in txt:
                    if (ch.isalpha() or ch in (" ", "-", "_")) and len(self._name) < MAX_NAME_LEN:
                        self._name += ch
                        self._error = ""

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    name = self._name.strip()
                    if not name:
                        self._error = "O nome nao pode estar vazio."
                        return
                    # Vai para a selecao de personagem
                    from states.select_state import SelectState
                    self.game.state_manager.change(SelectState(self.game, name.upper()))

                elif event.key == pygame.K_ESCAPE:
                    from states.title_state import TitleState
                    self.game.state_manager.change(TitleState(self.game))

                elif event.key == pygame.K_BACKSPACE:
                    self._name  = self._name[:-1]
                    self._error = ""

                else:
                    # Keep legacy KEYDOWN unicode handling as fallback
                    char = getattr(event, 'unicode', '')
                    if char and (char.isalpha() or char in (" ", "-", "_")):
                        if len(self._name) < MAX_NAME_LEN:
                            self._name += char
                            self._error = ""

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # on mobile provide OK and DEL buttons under the input box
                # Also open the soft keyboard if the user taps the input box
                W, H = (640, 360)
                try:
                    surf = pygame.display.get_surface()
                    if surf:
                        W, H = surf.get_size()
                except Exception:
                    pass

                box_w, box_h = 280, 32
                box_x = W // 2 - box_w // 2
                box_y = H // 2 - box_h // 2
                if getattr(self.game, 'mobile', False):
                    if self._ok_rect and self._ok_rect.collidepoint(event.pos):
                        name = self._name.strip()
                        if not name:
                            self._error = "O nome nao pode estar vazio."
                            return
                        from states.select_state import SelectState
                        self.game.state_manager.change(SelectState(self.game, name.upper()))
                    elif self._del_rect and self._del_rect.collidepoint(event.pos):
                        self._name = self._name[:-1]
                        self._error = ""
                    else:
                        # Tap on the input box opens soft keyboard
                        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
                        if box_rect.collidepoint(event.pos):
                            try:
                                pygame.key.start_text_input()
                                self._text_input_active = True
                            except Exception:
                                pass
                else:
                    # Desktop: clicking ok/del still works
                    if self._ok_rect and self._ok_rect.collidepoint(event.pos):
                        name = self._name.strip()
                        if not name:
                            self._error = "O nome nao pode estar vazio."
                            return
                        from states.select_state import SelectState
                        self.game.state_manager.change(SelectState(self.game, name.upper()))
                    elif self._del_rect and self._del_rect.collidepoint(event.pos):
                        self._name = self._name[:-1]
                        self._error = ""

            # ignore other events

    def update(self, dt):
        self._blink_timer += dt
        if self._blink_timer >= 0.55:
            self._blink_timer = 0.0
            self._cursor_on   = not self._cursor_on

    def draw(self, screen):
        W, H = screen.get_size()
        font_title = get_font("Courier New", 28, bold=True)
        font       = get_font("Courier New", 18)

        title = font_title.render("DIGITE SEU NOME", True, WHITE)
        screen.blit(title, (W // 2 - title.get_width() // 2, H // 4))

        # Caixa de entrada
        box_w, box_h = 280, 32
        box_x = W // 2 - box_w // 2
        box_y = H // 2 - box_h // 2
        pygame.draw.rect(screen, (40, 40, 40), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, WHITE,        (box_x, box_y, box_w, box_h), 1)

        cursor  = "|" if self._cursor_on else " "
        display = font.render(self._name + cursor, True, WHITE)
        screen.blit(display, (box_x + 8, box_y + 6))

        # Erro
        if self._error:
            err = font.render(self._error, True, RED)
            screen.blit(err, (W // 2 - err.get_width() // 2, box_y + box_h + 10))

        # Draw mobile OK / DEL buttons beneath the input box if mobile
        if getattr(self.game, 'mobile', False):
            btn_w, btn_h = 80, 28
            gap = 12
            ok_x = W // 2 + gap
            ok_y = box_y + box_h + 36
            del_x = W // 2 - btn_w - gap
            del_y = ok_y
            self._ok_rect = pygame.Rect(ok_x, ok_y, btn_w, btn_h)
            self._del_rect = pygame.Rect(del_x, del_y, btn_w, btn_h)
            pygame.draw.rect(screen, (50, 150, 50), self._ok_rect)
            pygame.draw.rect(screen, (150, 50, 50), self._del_rect)
            ok_txt = font.render("OK", True, WHITE)
            del_txt = font.render("DEL", True, WHITE)
            screen.blit(ok_txt, (ok_x + (btn_w - ok_txt.get_width()) // 2, ok_y + 4))
            screen.blit(del_txt, (del_x + (btn_w - del_txt.get_width()) // 2, del_y + 4))

        # Dicas
        hint = get_font("Courier New", 13).render(
            "ENTER confirmar     ESC voltar", True, GRAY
        )
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 30))

    def on_exit(self):
        # Stop text input (hide keyboard) when leaving the state
        try:
            if getattr(self, '_text_input_active', False):
                pygame.key.stop_text_input()
                self._text_input_active = False
        except Exception:
            pass
