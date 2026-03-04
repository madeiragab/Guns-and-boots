from entities.character import Character


class Enemy(Character):
    """AI-controlled enemy."""

    PROFILES = {
        "GRUNT": {
            "hp": 22, "atk": 5, "defense": 1,
            "sprite": None,
        },
        "HEAVY": {
            "hp": 35, "atk": 8, "defense": 3,
            "sprite": None,
        },
        "SNIPER": {
            "hp": 18, "atk": 10, "defense": 1,
            "sprite": None,
        },
    }

    def __init__(self, profile="GRUNT"):
        data = self.PROFILES.get(profile, self.PROFILES["GRUNT"])
        super().__init__(
            name=profile,
            hp=data["hp"],
            atk=data["atk"],
            defense=data["defense"],
        )
        self.profile = profile
