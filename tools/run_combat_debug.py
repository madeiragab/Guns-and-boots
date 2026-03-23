"""Run quick, headless combat simulations to inspect HP transitions.

Usage (from project root):
    python tools/run_combat_debug.py
"""
import sys
import os

# Garante que a raiz do projeto esteja no sys.path e o CWD seja a raiz
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from entities.enemy import Enemy
from entities.character import Character
from systems.combat import resolve_action


def quick_demo():
    p = Character("PLAYER", hp=20, atk=6, defense=1)
    e = Enemy("GRUNT")

    print("=== Starting battle demo ===")
    print(f"Player HP: {p.hp} / {p.max_hp}")
    print(f"Enemy  HP: {e.hp} / {e.max_hp}")

    # Jogador atira
    logs = resolve_action(p, e, "shoot")
    for l in logs:
        print(l)
    print(f"After player action: Enemy HP = {e.hp}")

    # Inimigo age
    logs = resolve_action(e, p, "shoot")
    for l in logs:
        print(l)
    print(f"After enemy action: Player HP = {p.hp}")

    # Jogador usa especial
    logs = resolve_action(p, e, "special")
    for l in logs:
        print(l)
    print(f"After special: Enemy HP = {e.hp}")


if __name__ == "__main__":
    quick_demo()
