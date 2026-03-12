import random


def choose_action(enemy, player):
    """
    Rule-based AI.  Returns one of: "shoot", "cover", "special", "medkit"
    """
    hp_ratio = enemy.hp / enemy.max_hp
    is_boss = getattr(enemy, '_is_boss', False)

    # Prioritise healing if badly wounded and medkits available
    if hp_ratio < 0.30 and enemy.medkits > 0:
        if random.random() < 0.65:
            return "medkit"

    # Cool down if overheated
    if enemy.heat >= 8:
        if random.random() < 0.55:
            return "cover"

    # Check which actions are available
    can_special = getattr(enemy, 'special_cooldown', 0) <= 0

    # Bosses use specials more aggressively
    if is_boss and can_special:
        roll = random.random()
        if roll < 0.45:
            return "shoot"
        elif roll < 0.65:
            return "cover"
        else:
            return "special"
    elif can_special:
        roll = random.random()
        if roll < 0.70:
            return "shoot"
        elif roll < 0.90:
            return "cover"
        else:
            return "special"
    else:
        roll = random.random()
        if roll < 0.75:
            return "shoot"
        else:
            return "cover"
