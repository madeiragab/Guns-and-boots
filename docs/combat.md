> 🇧🇷 [Português](combat.pt-BR.md) · 🇬🇧 **English**

# Combat System

All rules live in `systems/combat.py` and `entities/character.py`.
Everything below is the exact behavior of the code.

## Actions

Each turn, a combatant picks one of four actions:

| Action | Effect | Heat | Notes |
|---|---|---:|---|
| **SHOOT** | `atk + rand(-1, 2) − def` damage (min 1) | +2 | Can jam when overheated |
| **SPECIAL** | `(atk + rand(2, 5) − def, min 1) × 2` damage | +4 | 2-turn cooldown, even on miss/jam |
| **COVER** | Blocks: −2 damage taken and halves enemy hit chance | −3 | Consumed by the next hit received |
| **MEDKIT** | Heals +10 HP | 0 | 1 per battle (refilled by `reset_for_battle`) |

## Hit chance

```text
chance = 0.75 + (attacker.atk − defender.def) × 0.03
chance = clamp(chance, 0.20, 0.95)
if defender is in cover: chance × 0.5
```

A strong attacker against a weak defender caps at 95%; even a hopeless
matchup keeps a 20% floor — no attack is ever guaranteed or impossible.

## Heat and jamming

Heat is the risk/reward mechanic that keeps spamming SHOOT/SPECIAL from
being optimal:

- Heat is capped at **10**. SHOOT adds 2, SPECIAL adds 4, COVER removes 3.
- At **heat ≥ 8** the weapon can **jam** when firing:

  | Heat | Jam chance |
  |---:|---:|
  | 8 | 10% |
  | 9 | 25% |
  | 10 | 40% |

- A jammed SHOOT wastes the turn (+1 heat). A jammed SPECIAL wastes the
  turn **and** triggers the 2-turn cooldown (+2 heat).

The optimal loop is therefore: pressure with shots, watch the heat gauge,
and weave COVER in — which simultaneously cools the weapon, absorbs damage
and halves the enemy's next hit chance.

## Enemy AI (`systems/ai.py`)

### Regular enemies and bosses

Priority rules, evaluated top to bottom:

1. **HP < 30% and has medkit** → 65% chance to heal.
2. **Heat ≥ 8** → 55% chance to take cover.
3. Otherwise, a weighted roll:
   - regular enemy: 70% shoot / 20% cover / 10% special;
   - **boss**: 45% shoot / 20% cover / **35% special** (more aggressive);
   - if special is on cooldown: 75% shoot / 25% cover.

### Final boss (utility scoring)

The final boss uses a different brain (`_choose_final_boss_action`):

1. **Guaranteed-kill windows** — if a shot or special can finish the
   player this turn, always take it.
2. **Survival** — below 25% HP it heals (or covers first if overheated);
   at heat ≥ 9 it cools down, occasionally punishing a wounded player
   with a special anyway.
3. Otherwise every available action gets an **expected-damage score**
   (`_expected_damage`) adjusted by context: specials are worth more
   against a healthy player, shooting into cover is penalized, healing at
   high HP is heavily penalized.
4. It then picks randomly among all actions within 1.0 point of the best
   score — strong play that stays slightly unpredictable.

## Player boss form (final battle comeback)

During the final boss fight the player can trigger a **one-time
transformation** (`Player.activate_final_boss_form`):

- max HP × 1.6 + 20 (at least +35), full heal;
- ATK +5 (at least ×1.5), DEF +2 (at least ×1.4);
- +1 medkit, heat zeroed, cooldowns cleared;
- sprites and projectiles swap to the matching Boss folder.

Stats and visuals are restored after the battle
(`revert_from_boss_form`).
