# Guns and Boots

A retro-futuristic 2D turn-based game built with Python and Pygame — with a
heat/jam gambling mechanic, rule-based enemy AI and a final-battle
transformation system.

**Made by Gabriel Madeira**

> Project developed for the **Special Topics** course in the **Computer Science** program at **IFSulDeMinas**.

## Documentation

| Doc | What's inside |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Layers, state machine, main loop, audio, save system |
| [docs/combat.md](docs/combat.md) | Every combat formula: hit chance, heat/jam, AI behavior |
| [docs/adding-characters.md](docs/adding-characters.md) | How to add characters/bosses without touching code |
| [docs/build.md](docs/build.md) | Windows .exe build, Android APK, CI |

---

## Requirements

```bash
pip install pygame
```

## How To Run

```bash
python main.py
```

Install dependencies from the project file:

```bash
pip install -r requirements.txt
```

## Build & Mobile (quick)

This project supports a desktop release workflow and a prepared mobile package.

- Run locally (desktop):

```powershell
python main.py
```

- Run in mobile simulation mode (adjusts UI/input for touch):

```powershell
python main.py --mobile
```

- Create a Windows release (uses the project's virtualenv if present):

```powershell
.\build.bat
```

- Prepare mobile package (does not build APK, creates `mobile_package` with instructions):

```powershell
.\build.bat apk
```

Notes:
- Building an APK requires external toolchains (Buildozer or Briefcase) and is not performed automatically by `build.bat`.
- The `mobile_package/README-mobile.txt` contains steps to continue on a Linux/WSL or other Android-capable environment.

Touch controls (mobile mode):
- Tap action buttons at bottom: `ATIRAR`, `COBERTURA`, `ESPECIAL`, `MEDKIT`.
- Menus: tap items to select; `OK` / `DEL` buttons appear on name input screen.

Quick test (headless smoke test):

```powershell
& .venv\Scripts\python.exe tools/run_test.py
```
Should print `RUN_OK` when successful.

---

## Controls

| Key | Action |
|---|---|
| Up / Down | Navigate menus |
| Left / Right | Navigate character selection |
| Enter | Confirm |
| Esc | Back / Quit |

---

## Game Flow

```text
Title Screen
  |- (no save) -> Enter name -> Choose character -> Hub
  '- (with save) -> CONTINUE (saved name) or NEW GAME

Hub
  |- BATTLE -> fight regular enemies in sequence
  |- CHANGE CHARACTER -> return to character selection
  '- EXIT

Battle vs Enemies -> Result -> next enemy
  '- all defeated -> DANGER screen -> Boss Battle

Boss Battle -> Result
  '- all bosses defeated -> Credits -> Title Screen (free mode saved)

Free Mode (after finishing the game)
  '- Hub -> BATTLE selects a random boss indefinitely
```

---

## Systems

### State Machine (`core/state_manager.py`)
Handles all screens as stackable states. Supports `change`, `push`, and `pop`. Every state transition notifies the `Game` object so the soundtrack can be updated automatically.

### Save System (`core/game.py`)
Saves and loads progress through `save.json`:
- Player name
- Unlocked characters
- Defeated bosses
- Enemy round progression
- `completed` flag for post-game mode

After finishing the game, the save is kept with `completed = True` and all characters unlocked. The save is deleted only if the player chooses `NEW GAME` on the title screen.

### Combat System (`systems/combat.py`)
Turn-based combat with the following actions:

| Action | Effect | Heat |
|---|---|---:|
| SHOOT | `atk + rand(-1,2) - enemy def` | +2 |
| COVER | Reduces incoming damage and lowers hit chance against the defender | -3 |
| SPECIAL | `(atk + rand(2,5) - def) * 2` | +4 |
| MEDKIT | Restores HP (1 use per battle) | 0 |

**Heat / Jam System:** when heat is `>= 8`, the weapon can jam. Cover helps cool the weapon down.

### Enemy AI (`systems/ai.py`)
Rule-based AI that considers:
- Current HP -> heals when badly wounded
- Weapon heat -> uses cover when overheated
- Enemy type -> bosses use specials more aggressively

The **final boss** uses a separate utility-scoring brain: it detects
guaranteed-kill windows, weighs expected damage per action and stays
slightly unpredictable by picking among near-best options. Details in
[docs/combat.md](docs/combat.md).

### Final Battle & Boss Form (`entities/final_boss.py`, `states/final_danger_state.py`)
After all bosses fall, a final gauntlet begins. During the final battle the
player can trigger a **one-time boss-form transformation** — a comeback
mechanic that boosts stats, refills heat/cooldowns and swaps the sprites to
the character's boss visuals. Everything reverts when the battle ends.

### Sprite Animator (`core/sprite_animator.py` and `ui/sprite_loader.py`)
Loads PNG frames from subfolders such as `idle`, `shoot`, `cover`, `damage`, `medkit`, and `special/anim`. Supports looping and one-shot animations with automatic return to idle, plus scaling, colorkey, and configurable FPS.

### Projectile System (`entities/projectile.py`)
Projectiles travel from attacker to target in real time (`0.35s`). Damage is only resolved when the projectile reaches the target through the `on_hit` callback.

### Audio System (`core/game.py`)
Managed centrally by the `Game` object:
- `theme.mp3` -> loops on the title screen and credits
- `battle music1.mp3` / `battle music2.mp3` -> chosen randomly for battles
- `bullet.mp3` -> normal shot SFX
- `special.mp3` -> special ability SFX

### Characters And Bosses
Loaded dynamically from `assets/sprites/Players/` and `assets/sprites/Bosses/`. Each character folder contains its own animation subfolders. New characters can be added by creating a new folder, without code changes.

Defeated bosses are unlocked as playable characters.

---

## Project Structure

```text
Guns and boots/
|- main.py                  - entry point
|- requirements.txt         - dependencies
|- README.md
|- .gitignore
|
|- core/                    - game engine layer
|  |- game.py               - window, main loop, audio, save system
|  |- state_manager.py      - push/pop/change state machine
|  '- sprite_animator.py    - frame-based sprite animator
|
|- entities/                - gameplay objects
|  |- character.py          - base stats, heat, jam, cover
|  |- player.py             - player-controlled character + boss form
|  |- enemy.py              - regular enemies
|  |- boss.py               - bosses
|  |- final_boss.py         - final bosses
|  '- projectile.py         - animated projectile with on_hit callback
|
|- states/                  - game screens / states
|  |- base_state.py
|  |- title_state.py        - title screen
|  |- name_state.py         - name input
|  |- select_state.py       - character selection
|  |- hub_state.py          - hub / main menu
|  |- battle_state.py       - turn-based battle
|  |- danger_state.py       - transition before boss fight
|  |- final_danger_state.py - transition before the final boss gauntlet
|  |- result_state.py       - battle result screen
|  '- credits_state.py      - final credits screen
|
|- systems/                 - decoupled gameplay logic
|  |- combat.py             - resolve_action(), hit chance, damage
|  '- ai.py                 - rule-based enemy AI
|
|- ui/                      - visual UI components
|  |- button.py
|  |- healthbar.py
|  |- logbox.py
|  '- sprite_loader.py
|
|- assets/
|  |- sfx/                  - music and sound effects
|  |  |- theme.mp3
|  |  |- battle music1.mp3
|  |  |- battle music2.mp3
|  |  |- bullet.mp3
|  |  '- special.mp3
|  '- sprites/
|     |- Players/           - playable characters
|     |- Bosses/            - bosses
|     |- Enemy/             - regular enemies
|     |- field/             - battle backgrounds
|     '- bullet/            - default projectile frames
|
'- tools/                   - development scripts
   |- run_combat_debug.py   - terminal combat simulation
   |- run_test.py           - headless smoke test
   '- sprite_demo.py        - interactive sprite viewer
```
