from entities.character import Character


class Player(Character):
    """Human-controlled character."""

    def __init__(self, name="PLAYER"):
        super().__init__(name=name, hp=30, atk=7, defense=2)
