# Descent

Descent is a top-down 2D roguelite focused on deep build permutations and rapid-fire runs. This repository now ships a fully playable prototype built with [pygame-ce](https://www.pygame.org/ce/), including bespoke pixel art, 216 weapon variants, 12 playable characters, and adaptive enemy waves.

## Features

- **216 Attunable Weapons** – Element, manufacturer, and chassis permutations create hundreds of distinct firing patterns with unique palettes and stat curves.
- **12 Playable Divers** – Each character sports bespoke colors, stat spreads, and keyword affinities that steer your build path.
- **Adaptive Encounters** – Procedural waves scale enemy health, speed, and damage by stage while alternating behaviors (orbiters, strafers, chargers).
- **Diegetic Loot Drops** – Enemies have a chance to drop attunable artifacts; collect them mid-run to instantly swap your loadout.
- **Handcrafted Pixel Art Palette** – Characters, enemies, projectiles, and pickups use custom pixel glyphs tinted on the fly to reflect elemental energies.
- **Dive Lab Meta-Progression** – Bank Aether between dives to unlock permanent stat upgrades per diver, encouraging mastery-driven grinding across hundreds of runs.
- **Replay-Ready Telemetry** – Session stats track stage clears, damage dealt, damage taken, and post-run Aether earnings to reinforce mastery.

## Installation

1. Ensure you have Python 3.10–3.14 installed (the build is forward-compatible with Python 3.14 thanks to pygame-ce).
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
| `U` / `Tab` | Open the Dive Lab upgrades menu |
| `Enter` / `Space` | Confirm selection or restart after defeat |
| `Esc` / Window close | Quit |

## Gameplay Loop

1. **Dive Lab Meta Hub** – From character select, tap `Tab`/`U` to invest earned Aether into per-diver stat tracks (Vitality, Arsenal, Tempo, Focus) before diving back in.
2. **Character Select** – Browse the roster with the arrow keys and deploy with `Enter`. Each diver alters core stats (Integrity, Speed, Damage, Crit, Focus) and injects thematic keywords.
3. **Run Start** – Spawns begin at Stage 1 with multi-wave arenas bounded by reactive neon walls.
4. **Combat** – Hold and strafe while unleashing your attuned weapon. Fire rate, spread, projectile speed, magazine size, and reload windows depend on your attunement.
5. **Loot & Permutations** – Enemies may drop new weapons. Interact to instantly respec your attack profile mid-wave.
6. **Stage Escalation** – Survive three waves to heal, escalate to the next stage, and face faster, tougher foes.
7. **Telemetry & Rewards** – Upon defeat, review run stats, bank your Aether payout toward permanent upgrades, and instantly re-queue a new permutation-rich attempt.

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
├── meta.py                 # Persistent Dive Lab meta-progression utilities
├── weapon.py               # Weapon runtime logic and cooldown handling
└── weapon_data.py          # Procedural weapon catalog generation (216 variants)
```

Additional design documentation remains in the `docs/` directory for reference and future iteration.

## Roadmap

### Q1 Goals – Deepen Core Loop
- Expand arenas with modular room tiles, turret sockets, and reactive hazards to diversify movement puzzles.
- Prototype elite enemy variants with affix-style modifiers (Shielded, Spore Host, Overcharged) that synergize with weapon keywords.
- Ship first-pass sound design using open-licensed sfx beds and an adaptive soundtrack stem system.

### Q2 Goals – Broaden Meta & Progression
- Layer in diver-specific questlines that unlock ultimate abilities and cosmetic suits after milestone achievements.
- Introduce a relic forge that consumes duplicate weapons to roll persistent relic perks, increasing long-term grind appeal.
- Stand up weekly challenge dives with seeded permutations, leaderboard telemetry, and rotating mutators.

### Q3 Goals – Productionization
- Integrate online stat-sync/backups for the Dive Lab save file alongside configurable cloud paths.
- Build a tutorialized onboarding experience with ghost replays that teach dodge timing and pickup prioritization.
- Target Steam Deck certification with revised input prompts, haptics, and performance budgets.

Enjoy diving the Descent and exploring the countless permutations! ⚔️

