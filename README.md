# Guns and Boots

A retro-futuristic 2D turn-based combat game built with Python + Pygame.

## Requirements

```
pip install pygame
```

## Run

```
python main.py
```

## Controls

| Key      | Action           |
|----------|------------------|
| ↑ / ↓    | Navigate menus   |
| ENTER    | Confirm          |
| ESC      | Back / Quit      |

## Project structure

```
main.py
core/
    game.py            – window, main loop (60 FPS)
    state_manager.py   – push/pop/change state machine
states/
    base_state.py
    title_state.py     – TITLE screen
    name_state.py      – NAME_INPUT screen
    hub_state.py       – HUB_MENU screen
    battle_state.py    – BATTLE screen
    result_state.py    – RESULT screen
entities/
    character.py       – base stats + heat/jam logic
    player.py
    enemy.py           – GRUNT / HEAVY / SNIPER profiles
systems/
    combat.py          – resolve_action()
    ai.py              – rule-based enemy AI
ui/
    button.py
    healthbar.py
    logbox.py
assets/
    fonts/
    sprites/
```

## Combat actions

| Action     | Effect                                    | Heat |
|------------|-------------------------------------------|------|
| SHOOT      | atk + rand(-1,2) – enemy.def              | +2   |
| TAKE COVER | cover = True, reduce incoming damage      | -3   |
| OVERCHARGE | atk + rand(2,5) – enemy.def               | +4   |
| MEDKIT     | +10 HP (limited to 3 per battle)          |  0   |

Heat ≥ 8 → chance of weapon jam (attack fails).
