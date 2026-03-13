class StateManager:
    """Manages game states. Supports push/pop for overlay states and change for full transitions."""

    def __init__(self):
        self._stack = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _current(self):
        return self._stack[-1] if self._stack else None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def change(self, new_state):
        """Replace the current state with a new one."""
        if self._stack:
            self._stack[-1].on_exit()
            self._stack.pop()
        self._stack.append(new_state)
        new_state.on_enter()
        game = getattr(new_state, "game", None)
        if game is not None and hasattr(game, "on_state_changed"):
            game.on_state_changed(new_state)

    def push(self, new_state):
        """Push a new state on top (current state is paused, not destroyed)."""
        if self._stack:
            self._stack[-1].on_pause()
        self._stack.append(new_state)
        new_state.on_enter()
        game = getattr(new_state, "game", None)
        if game is not None and hasattr(game, "on_state_changed"):
            game.on_state_changed(new_state)

    def pop(self):
        """Remove the top state and resume the one below."""
        if self._stack:
            self._stack[-1].on_exit()
            self._stack.pop()
        if self._stack:
            self._stack[-1].on_resume()
            resumed = self._stack[-1]
            game = getattr(resumed, "game", None)
            if game is not None and hasattr(game, "on_state_changed"):
                game.on_state_changed(resumed)

    # ------------------------------------------------------------------
    # Forwarded calls
    # ------------------------------------------------------------------
    def handle_events(self, events):
        state = self._current()
        if state:
            state.handle_events(events)

    def update(self, dt):
        state = self._current()
        if state:
            state.update(dt)

    def draw(self, screen):
        state = self._current()
        if state:
            state.draw(screen)

    def is_empty(self):
        return len(self._stack) == 0
