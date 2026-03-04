import random


def choose_action(enemy, player):
    """
    Rule-based AI.  Returns one of: "shoot", "cover", "overcharge", "medkit"
    """
    hp_ratio = enemy.hp / enemy.max_hp

    # Prioritise healing if badly wounded and medkits available
    if hp_ratio < 0.30 and enemy.medkits > 0:
        if random.random() < 0.65:
            return "medkit"

    # Cool down if overheated
    if enemy.heat >= 8:
        if random.random() < 0.55:
            return "cover"

    # Normal decision weights: 70% shoot, 20% cover, 10% overcharge
    roll = random.random()
    if roll < 0.70:
        return "shoot"
    elif roll < 0.90:
        return "cover"
    else:
        return "overcharge"
