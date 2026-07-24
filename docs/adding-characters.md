# Adding Characters, Bosses and Enemies

Characters are **discovered from the file system at runtime** — no code
changes needed. Drop a new folder with the right structure and the game
picks it up.

## Folder structure

```text
assets/sprites/
├─ Players/
│  └─ <CharacterName>/          ← folder name = in-game name
│     ├─ idle/       idle0.png, idle1.png, ...      (loops)
│     ├─ shoot/      ...                            (one-shot)
│     ├─ cover/      ...
│     ├─ damage/     ...
│     ├─ medkit/     ...
│     └─ special/
│        ├─ anim/    frames of the special attack animation
│        └─ bullet/  frames of the special projectile (natural size)
├─ Bosses/
│  └─ <BossName>/               ← same structure as Players
├─ Enemy/                       ← regular enemies
├─ field/                       ← battle backgrounds
└─ bullet/                      ← default projectile frames (shared)
```

## Rules and behavior

- **Frames** are PNG files loaded in alphabetical order — use zero-padded
  names (`idle00.png`, `idle01.png`…) to keep ordering stable.
- Animations play at **12 FPS**; `idle` loops, everything else plays once
  and returns to idle automatically.
- Player/boss frames are scaled to **160×160**; pure black `(0, 0, 0)` is
  used as the transparency colorkey.
- Missing folders are fine: if `special/bullet/` doesn't exist, the shared
  default bullet is used; if a character has no animations at all, a solid
  placeholder is rendered instead of crashing.
- **Boss unlock**: bosses defeated in the campaign become playable — the
  game unlocks them by name, so a folder in `Bosses/<Name>` that matches a
  `Players/<Name>` folder gives the character its boss-form visuals for
  the final-battle transformation.
- The starter character is defined by `DEFAULT_STARTER_PLAYER` in
  `core/game.py` (default: `Pablo`). Mandatory battle rosters are set in
  `states/final_danger_state.py` (`MANDATORY_BOSSES`,
  `MANDATORY_FINAL_BOSSES`).

## Checklist for a new playable character

1. Create `assets/sprites/Players/MyChar/` with at least an `idle/` folder.
2. Add `shoot/`, `cover/`, `damage/`, `medkit/`, `special/anim/` and
   `special/bullet/` as you produce the art.
3. Run the sprite viewer to check the result:

   ```bash
   python tools/sprite_demo.py
   ```

4. Unlock it in-game (finish the campaign) or add it temporarily to
   `unlocked_players` in `save.json` for testing.
