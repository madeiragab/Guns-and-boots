"""Run quick, headless combat simulations to inspect HP transitions.

Usage:
    python run_combat_debug.py

This will run a few example turns and print resolve_action logs to stdout.
"""
from entities.enemy import Enemy
from entities.character import Character
from systems.combat import resolve_action


def quick_demo():
    p = Character("PLAYER", hp=20, atk=6, defense=1)
    e = Enemy("GRUNT")

    print("=== Starting battle demo ===")
    print(f"Player HP: {p.hp} / {p.max_hp}")
    print(f"Enemy  HP: {e.hp} / {e.max_hp}")

    # Player shoots
    logs = resolve_action(p, e, "shoot")
    for l in logs:
        print(l)
    print(f"After player action: Enemy HP = {e.hp}")

    # Enemy acts
    logs = resolve_action(e, p, "shoot")
    for l in logs:
        print(l)
    print(f"After enemy action: Player HP = {p.hp}")

    # Player overcharges
    logs = resolve_action(p, e, "overcharge")
    for l in logs:
        print(l)
    print(f"After overcharge: Enemy HP = {e.hp}")


if __name__ == "__main__":
    quick_demo()
