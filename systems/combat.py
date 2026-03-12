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

    if action == "shoot":
        if attacker.check_jam():
            attacker.add_heat(1)
            logs.append(f"{attacker.name}: ARMA TRAVOU! Ataque falhou.")
            return logs

        hit_chance = _compute_hit_chance(attacker, defender)
        if random.random() > hit_chance:
            attacker.add_heat(2)
            logs.append(f"{attacker.name} atirou e ERROU!  (calor {attacker.heat})")
            return logs

        dmg = attacker.atk + random.randint(-1, 2) - defender.defense
        dmg = max(1, dmg)
        before = defender.hp
        defender.take_damage(dmg)
        after = defender.hp
        attacker.add_heat(2)
        logs.append(f"{attacker.name} atirou  →  {dmg} dano  (calor {attacker.heat})")
        logs.append(f"    {defender.name} HP: {before} → {after}")
        if attacker.heat >= 8:
            logs.append(f"  AVISO: arma de {attacker.name} SUPERAQUECENDO!")

    elif action == "special":
        if attacker.check_jam():
            attacker.add_heat(2)
            logs.append(f"{attacker.name}: ESPECIAL TRAVOU! Arma superaqueceu.")
            attacker.special_cooldown = 2
            return logs

        hit_chance = _compute_hit_chance(attacker, defender)
        if random.random() > hit_chance:
            attacker.add_heat(4)
            logs.append(f"{attacker.name} ESPECIAL ERROU!  (calor {attacker.heat})")
            attacker.special_cooldown = 2
            return logs

        dmg = attacker.atk + random.randint(2, 5) - defender.defense
        dmg = max(1, dmg) * 2
        before = defender.hp
        defender.take_damage(dmg)
        after = defender.hp
        attacker.add_heat(4)
        attacker.special_cooldown = 2
        logs.append(f"{attacker.name} ESPECIAL  →  {dmg} dano  (calor {attacker.heat})")
        logs.append(f"    {defender.name} HP: {before} → {after}")
        if attacker.heat >= 8:
            logs.append(f"  CALOR CRITICO: {attacker.name} esta em perigo!")

    elif action == "cover":
        attacker.cover = True
        attacker.reduce_heat(3)
        logs.append(f"{attacker.name} se cobriu.  (calor {attacker.heat})")

    elif action == "medkit":
        if attacker.medkits <= 0:
            logs.append(f"{attacker.name} nao tem medkits!")
        else:
            attacker.medkits -= 1
            attacker.heal(10)
            logs.append(
                f"{attacker.name} usou MEDKIT  →  +10 HP  ({attacker.medkits} restante)"
            )

    return logs
