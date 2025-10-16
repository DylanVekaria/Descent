# Descent

Descent is a top-down 2D roguelite focused on deep build permutations and rapid-fire runs. This repository now ships a fully playable prototype built with [pygame](https://www.pygame.org/), including bespoke pixel art, 216 weapon variants, 12 playable characters, and adaptive enemy waves.

## Features

- **216 Attunable Weapons** – Element, manufacturer, and chassis permutations create hundreds of distinct firing patterns with unique palettes and stat curves.
- **12 Playable Divers** – Each character sports bespoke colors, stat spreads, and keyword affinities that steer your build path.
- **Adaptive Encounters** – Procedural waves scale enemy health, speed, and damage by stage while alternating behaviors (orbiters, strafers, chargers).
- **Diegetic Loot Drops** – Enemies have a chance to drop attunable artifacts; collect them mid-run to instantly swap your loadout.
- **Handcrafted Pixel Art Palette** – Characters, enemies, projectiles, and pickups use custom pixel glyphs tinted on the fly to reflect elemental energies.
- **Replay-Ready Telemetry** – Session stats track stage clears, damage dealt, and damage taken to reinforce mastery.

## Installation

1. Ensure you have Python 3.10+ installed.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the game:

   ```bash
   python -m descent
   ```

## Controls

| Input | Action |
| ----- | ------ |
| `WASD` / Arrow Keys | Move the diver |
| Mouse | Aim |
| Left Mouse Button | Fire current weapon |
| `E` | Attune to the highlighted weapon pickup |
| `Enter` / `Space` | Confirm selection or restart after defeat |
| `Esc` / Window close | Quit |

## Gameplay Loop

1. **Character Select** – Browse the roster with the arrow keys and deploy with `Enter`. Each diver alters core stats (Integrity, Speed, Damage, Crit, Focus) and injects thematic keywords.
2. **Run Start** – Spawns begin at Stage 1 with multi-wave arenas bounded by reactive neon walls.
3. **Combat** – Hold and strafe while unleashing your attuned weapon. Fire rate, spread, projectile speed, magazine size, and reload windows depend on your attunement.
4. **Loot & Permutations** – Enemies may drop new weapons. Interact to instantly respec your attack profile mid-wave.
5. **Stage Escalation** – Survive three waves to heal, escalate to the next stage, and face faster, tougher foes.
6. **Telemetry** – Upon defeat, review run stats and instantly re-queue a new permutation-rich attempt.

## Project Structure

```
src/descent/
├── art.py                  # Pixel glyph definitions and tint helpers
├── character_data.py       # Playable diver roster and stat blocks
├── constants.py            # Screen dimensions, color palette, and layering
├── entities.py             # Sprite implementations for player, enemies, pickups, projectiles
├── enemy_data.py           # Enemy profiles and stage scaling tables
├── game.py                 # Core game loop, UI rendering, wave management
├── main.py                 # Entry point for running the game module
├── weapon.py               # Weapon runtime logic and cooldown handling
└── weapon_data.py          # Procedural weapon catalog generation (216 variants)
```

Additional design documentation remains in the `docs/` directory for reference and future iteration.

## Roadmap

- Expand arenas with modular room tiles and interactive hazards.
- Layer in meta-progression (unlockable characters, weapon blueprints, relic systems).
- Introduce bosses that leverage the permutation system with multi-phase patterns.
- Add audio design (sfx + reactive music) to reinforce combat readability.

Enjoy diving the Descent and exploring the countless permutations! ⚔️

