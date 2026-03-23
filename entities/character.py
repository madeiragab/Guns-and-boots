import random


class Character:
    """Base class for player and enemy."""

    def __init__(self, name, hp, atk, defense):
        self.name     = name
        self.max_hp   = hp
        self.hp       = hp
        self.atk      = atk
        self.defense  = defense
        self.heat     = 0
        self.cover    = False
        self.medkits  = 1
        self.special_cooldown = 0

    # ------------------------------------------------------------------
    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        if self.cover:
            amount = max(0, amount - 2)   # cobertura absorve mais 2
        self.hp = max(0, self.hp - amount)
        self.cover = False                # cobertura consumida apos o acerto

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    # ------------------------------------------------------------------
    # Auxiliares de calor
    def add_heat(self, amount):
        self.heat = min(10, self.heat + amount)

    def reduce_heat(self, amount):
        self.heat = max(0, self.heat - amount)

    def check_jam(self):
        """Returns True if the weapon jams this action."""
        if self.heat >= 8:
            jam_chance = 0.10 + (self.heat - 8) * 0.15   # 10% em 8, 25% em 9, 40% em 10
            return random.random() < jam_chance
        return False

    # ------------------------------------------------------------------
    def reset_for_battle(self):
        self.hp      = self.max_hp
        self.heat    = 0
        self.cover   = False
        self.medkits = 1
        self.special_cooldown = 0
