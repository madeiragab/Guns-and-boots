import random


def _compute_hit_chance(attacker, defender):
    """Compute base hit chance (0..1) from attacker/def stats and caps."""
    base = 0.75
    modifier = (attacker.atk - defender.defense) * 0.03
    chance = base + modifier
    chance = max(0.2, min(0.95, chance))
    # If defender is in cover, reduce chance by 50%
    if defender.cover:
        chance *= 0.5
    return chance


def resolve_action(attacker, defender, action):
    """Execute one action. Returns list of log strings."""
    logs = []

    # If attacker is forced to skip this turn (e.g., after overcharge), consume and skip
    if getattr(attacker, "skip_next", False):
        attacker.skip_next = False
        logs.append(f"{attacker.name} is recovering and cannot act this turn.")
        return logs

    if action == "shoot":
        if attacker.check_jam():
            attacker.add_heat(1)
            logs.append(f"{attacker.name}: WEAPON JAM! Attack failed.")
            return logs

        hit_chance = _compute_hit_chance(attacker, defender)
        if random.random() > hit_chance:
            attacker.add_heat(2)
            logs.append(f"{attacker.name} fired and MISSED!  (heat {attacker.heat})")
            return logs

        dmg = attacker.atk + random.randint(-1, 2) - defender.defense
        dmg = max(1, dmg)
        before = defender.hp
        defender.take_damage(dmg)
        after = defender.hp
        attacker.add_heat(2)
        logs.append(f"{attacker.name} fired  →  {dmg} dmg  (heat {attacker.heat})")
        logs.append(f"    {defender.name} HP: {before} → {after}")
        if attacker.heat >= 8:
            logs.append(f"  WARNING: {attacker.name} weapon running HOT!")

    elif action == "overcharge":
        # powerful attack, but causes skip next turn
        if attacker.check_jam():
            attacker.add_heat(2)
            logs.append(f"{attacker.name}: OVERCHARGE JAM! Weapon overheated.")
            return logs

        hit_chance = _compute_hit_chance(attacker, defender)
        if random.random() > hit_chance:
            attacker.add_heat(4)
            logs.append(f"{attacker.name} OVERCHARGED and MISSED!  (heat {attacker.heat})")
            # still suffers heat and skip
            attacker.skip_next = True
            return logs

        dmg = attacker.atk + random.randint(2, 5) - defender.defense
        dmg = max(1, dmg) * 2
        before = defender.hp
        defender.take_damage(dmg)
        after = defender.hp
        attacker.add_heat(4)
        attacker.skip_next = True
        logs.append(f"{attacker.name} OVERCHARGED  →  {dmg} dmg  (heat {attacker.heat})")
        logs.append(f"    {defender.name} HP: {before} → {after}")
        if attacker.heat >= 8:
            logs.append(f"  CRITICAL HEAT: {attacker.name} is in danger!")

    elif action == "cover":
        # Take cover: reduces chance to be hit this round by 50% (handled in _compute_hit_chance)
        attacker.cover = True
        attacker.reduce_heat(3)
        logs.append(f"{attacker.name} took cover.  (heat {attacker.heat})")

    elif action == "medkit":
        if attacker.medkits <= 0:
            logs.append(f"{attacker.name} has no medkits left!")
        else:
            attacker.medkits -= 1
            attacker.heal(10)
            logs.append(
                f"{attacker.name} used MEDKIT  →  +10 HP  ({attacker.medkits} left)"
            )

    return logs
