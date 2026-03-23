class BaseState:
    """All states inherit from this."""

    def __init__(self, game):
        self.game = game

    # Ganchos de ciclo de vida ------------------------------------------
    def on_enter(self):   pass
    def on_exit(self):    pass
    def on_pause(self):   pass
    def on_resume(self):  pass

    # Metodos de quadro (devem ser sobrescritos) ------------------------
    def handle_events(self, events): pass
    def update(self, dt):            pass
    def draw(self, screen):          pass
