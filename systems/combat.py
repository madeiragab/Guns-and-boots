import random


def resolve_action(attacker, defender, action):
    """
    Execute one action. Returns a list of log strings.

    Actions: "shoot", "cover", "overcharge", "medkit"
    """
    logs = []

    if action == "shoot":
        if attacker.check_jam():
            attacker.add_heat(1)
            logs.append(f"{attacker.name}: WEAPON JAM! Attack failed.")
            return logs

        dmg = attacker.atk + random.randint(-1, 2) - defender.defense
        dmg = max(1, dmg)
        defender.take_damage(dmg)
        attacker.add_heat(2)
        logs.append(f"{attacker.name} fired  →  {dmg} dmg  (heat {attacker.heat})")
        if attacker.heat >= 8:
            logs.append(f"  WARNING: {attacker.name} weapon running HOT!")

    elif action == "overcharge":
        if attacker.check_jam():
            attacker.add_heat(2)
            logs.append(f"{attacker.name}: OVERCHARGE JAM! Weapon overheated.")
            return logs

        dmg = attacker.atk + random.randint(2, 5) - defender.defense
        dmg = max(1, dmg)
        defender.take_damage(dmg)
        attacker.add_heat(4)
        logs.append(f"{attacker.name} OVERCHARGED  →  {dmg} dmg  (heat {attacker.heat})")
        if attacker.heat >= 8:
            logs.append(f"  CRITICAL HEAT: {attacker.name} is in danger!")

    elif action == "cover":
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
                f"{attacker.name} used MEDKIT  →  +10 HP  "
                f"({attacker.medkits} left)"
            )

    return logs
