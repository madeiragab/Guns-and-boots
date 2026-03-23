import random


def _expected_damage(attacker, defender, action):
    if action == "special":
        base = (attacker.atk + 3.5 - defender.defense) * 2
        hit_chance = 0.75 + (attacker.atk - defender.defense) * 0.03
        heat_risk = 0.82 if attacker.heat >= 8 else 1.0
        return max(1.0, base) * max(0.2, min(0.95, hit_chance)) * heat_risk

    if action == "shoot":
        base = attacker.atk + 0.5 - defender.defense
        hit_chance = 0.75 + (attacker.atk - defender.defense) * 0.03
        heat_risk = 0.80 if attacker.heat >= 8 else 1.0
        return max(1.0, base) * max(0.2, min(0.95, hit_chance)) * heat_risk

    if action == "medkit":
        missing_hp = max(0, attacker.max_hp - attacker.hp)
        return min(10, missing_hp) * 1.8

    if action == "cover":
        threat = max(1.0, defender.atk - attacker.defense)
        heat_pressure = 1.2 if attacker.heat >= 8 else 1.0
        return threat * 3.0 * heat_pressure

    return 0.0


def _choose_final_boss_action(enemy, player):
    hp_ratio = enemy.hp / max(1, enemy.max_hp)
    player_ratio = player.hp / max(1, player.max_hp)
    can_special = getattr(enemy, "special_cooldown", 0) <= 0

    # Janelas de abate garantido: sempre aproveite.
    shoot_kill = player.hp <= max(1, enemy.atk - player.defense)
    special_kill = can_special and player.hp <= max(2, (enemy.atk + 2 - player.defense) * 2)
    if special_kill:
        return "special"
    if shoot_kill:
        return "shoot"

    # Logica critica de sobrevivencia.
    if hp_ratio < 0.25 and enemy.medkits > 0:
        if enemy.heat >= 8:
            return "cover"
        return "medkit"

    if enemy.heat >= 9:
        # Alterna entre resfriar e pressionar para evitar turnos gratis.
        if can_special and player_ratio < 0.45 and random.random() < 0.35:
            return "special"
        return "cover"

    candidates = ["shoot", "cover"]
    if can_special:
        candidates.append("special")
    if enemy.medkits > 0:
        candidates.append("medkit")

    # Bonus de utilidade sensiveis ao contexto.
    scored = []
    for action in candidates:
        score = _expected_damage(enemy, player, action)

        if action == "special":
            if player_ratio > 0.65:
                score += 4.0
            if enemy.heat >= 7:
                score -= 2.2

        if action == "shoot":
            if player.cover:
                score -= 2.8

        if action == "cover":
            if player_ratio < 0.30:
                score -= 2.0

        if action == "medkit":
            if hp_ratio > 0.70:
                score -= 8.0
            if hp_ratio < 0.45:
                score += 3.5

        scored.append((score, action))

    scored.sort(reverse=True)

    # Mantem decisoes fortes, permanecendo levemente imprevisivel.
    top_score = scored[0][0]
    top_actions = [action for score, action in scored if score >= top_score - 1.0]
    return random.choice(top_actions)


def choose_action(enemy, player):
    """
    Rule-based AI.  Returns one of: "shoot", "cover", "special", "medkit"
    """
    hp_ratio = enemy.hp / enemy.max_hp
    is_boss = getattr(enemy, '_is_boss', False)
    is_final_boss = getattr(enemy, '_is_final_boss', False)

    if is_final_boss:
        return _choose_final_boss_action(enemy, player)

    # Prioriza cura se estiver muito ferido e houver kits medicos
    if hp_ratio < 0.30 and enemy.medkits > 0:
        if random.random() < 0.65:
            return "medkit"

    # Resfria se estiver superaquecido
    if enemy.heat >= 8:
        if random.random() < 0.55:
            return "cover"

    # Verifica quais acoes estao disponiveis
    can_special = getattr(enemy, 'special_cooldown', 0) <= 0

    # Chefes usam especiais de forma mais agressiva
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
