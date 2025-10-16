# Project "Descent" Game Design Document

## Vision Statement
Create a top-down 2D roguelite where every run feels bespoke through deep build permutations, adaptive encounters, and narrative-reactive systems. Players descend through biome-shifting layers influenced by their previous choices, wielding hundreds of modular weapons and dozens of characters with asymmetrical stat spreads and origin perks.

## Target Experience
- **Session Length**: 20–35 minutes per successful run.
- **Input**: Twin-stick (keyboard+mouse or controller); optional aim assist for accessibility.
- **Tone**: Dark techno-mystic world blending synthwave aesthetics with occult artifacts.
- **Audience**: Fans of Hades, Binding of Isaac, Nova Drift, and Vampire Survivors seeking deeper buildcraft.

## Core Pillars
1. **Build Permutation Playground** – Weapon modules, alt-fires, elemental infusions, and relic synergies produce radically different kits.
2. **Reactive World** – Biomes and enemy compositions morph based on prior successes and current build signatures.
3. **Meaningful Meta Layer** – Unlocks, factions, and codex research tie runs together without undermining tension.
4. **Readability & Responsiveness** – Crisp movement, generous animation cancel windows, and strong telegraphs keep deaths fair.

## Game Loop
1. **Between Runs (Hub: "The Atrium")**
   - Spend Ether Shards to unlock weapon frames, characters, and research trees.
   - Interact with faction NPCs to influence next run's modifiers (e.g., pact contracts).
   - Select a character + weapon frame (base archetype) + loadout charms.
2. **During Run**
   - Procedural node map with branching paths (inspired by Slay the Spire). Each node can be combat, event, shop, forge, or boss.
   - Clear rooms to earn drops: weapon modules, relics, stat infusions, and currencies.
   - Mid-run objectives triggered by faction agendas provide optional challenges.
3. **Post-Run**
   - Record telemetry, update faction influence meters, unlock codex entries, roll daily/weekly challenges.

## Systems Breakdown

### Characters (10+ Launch Archetypes)
Each character offers:
- **Base Stats**: Vitality, Resolve (shield), Alacrity (move speed), Focus (cooldown reduction), Flux (energy regen).
- **Signature Passive**: Run-altering mechanic (e.g., "Echo Diver" duplicates first module picked each biome).
- **Unique Starting Relic**: Encourages certain synergies but not mandatory.
- **Unlock Path**: Achievements or narrative quests ensure staggered reveal.

Example Archetypes:
1. **Axiom Warder** – Tanky, starts with barrier on room entry.
2. **Glimmer Wraith** – High crit chance, loses health if standing still.
3. **Circuit Savant** – Gains bonus module choices from tech pool.
4. **Rift Harvester** – Converts overkill damage into healing or ammo.
5. **Oracle of Ash** – Manipulates elemental status durations.

### Weapon System (100+ Weapons via Modular Templates)
- **Frames**: Base archetypes (Blade, Spear, Gun, Gauntlet, Catalyst, Drone, Glyph).
- **Modules**: Attachments altering attacks (projectile pattern, damage type, status application). Each weapon can host 3 core modules + 1 alt-fire.
- **Infusions**: Elemental overlays (Pyre, Frost, Volt, Void, Terra) that add DoTs, CC, or on-kill effects.
- **Masterwork Variants**: Rare drops that mutate behavior (e.g., chain lightning, boomerang arcs).
- **Crafting Currency**: During runs, players can reroll or fuse modules to chase synergies.
- **Balance Strategy**: Use parameterized data tables for quick tuning and ensure rarity tiers gate complexity.

### Relics & Augments
- **Relics** (Passive items): Provide stacking bonuses or trigger on specific conditions (e.g., gain shields when applying burn).
- **Sigils** (Active abilities): Charged by combat performance, unleash screen-clearing effects with cooldowns.
- **Gene Mods** (Stat infusions): Offer permanent run-long stat shifts with trade-offs.
- **Set Bonuses**: Collecting 3 items from a faction grants unique effect to encourage targeted builds.

### Signature Ability & Combo Engine
- **Ability Wheel**: Every diver wields a unique active ability (blink, overdrive, drone command, gravity wells, etc.) mapped to a shared cooldown input.
- **Combo Meter**: Consecutive kills extend a timer; hitting thresholds unlocks combo tiers that amplify damage, drone aggression, and drop rates.
- **Ability Synergy Tags**: Abilities read the current build state (weapon keywords, relic stacks) to subtly morph behavior (e.g., burn-focused builds increase nova DoT).
- **Meta Hooks**: Dive Lab upgrades and relics can shorten cooldowns, add shields on activation, or spawn additional drones to encourage buildcraft around actives.

### Drone & Support Systems
- **Support Drones**: Orbiting companions generated via abilities or relics fire auto-targeted projectiles scaled by combo tier and relic tags.
- **Field Effects**: Gravity wells, stasis zones, and healing blooms alter arena flow, rewarding positional mastery and giving defensive counterplay.
- **Dynamic Arena Events**: Timed supply drops, relic caches, or temporal fields inject moments of opportunistic decision-making mid-wave.

### Enemy & Encounter Design
- **Faction-Based Enemy Families**: Mechanist Constructs, Voidspawn, Cultists, Bio-Engineered Beasts.
- **AI Behaviors**: Emphasize readable windups, patterned bullet hell motifs, and synergy with status effects.
- **Adaptive Mutation System**: Enemy modifiers draw from deck influenced by player's dominant damage type and recent successes (e.g., anti-projectile shields if player uses heavy ranged).
- **Bosses**: Multi-phase with enrage triggers based on player choices (skipping objectives increases boss aggression).

### Procedural Generation & Level Flow
- **Biome Themes**: Neon Catacombs, Choking Gardens, Quantum Foundry, Echo Library, Chrono Abyss.
- **Node Graph**: Weighted randomization ensures at least two divergent routes per layer with hidden vaults accessible via keys.
- **Room Templates**: Designed with modular tile sets; hazards and cover adapt to player's mobility stats.
- **Event Deck**: Story-driven encounters offering choices with narrative consequences (e.g., side with a faction for future rewards but immediate curse).

### Progression & Meta Systems
- **Codex Research Tree**: Unlocks reveal new modules/relics and increase drop weight of underused content.
- **Faction Reputation**: Completing objectives shifts alliances, unlocking characters/weapons and altering encounter tables.
- **Daily/Weekly Mutators**: Rotating conditions (double boss, low gravity) for leaderboard runs.
- **Difficulty Sigils**: Optional toggles ("Ascension" levels) that add curses in exchange for higher rewards.

### Economy & Currencies
- **Run Currency**: Aetheric Orbs (shop), Scrap (crafting), Influence Tokens (faction objectives).
- **Meta Currency**: Ether Shards (unlock content), Lore Fragments (story scenes), Resonance Keys (permanent stat nodes).
- **Shops**: Offer rerolls, module crafting, healing, map info. Guarantee at least one item synergistic with current build via recommendation algorithm.

### UX & Feedback
- **HUD**: Clear display of active statuses, cooldowns, and RNG clarity (drop rates shown when hovering choices).
- **Build Codex**: Pause menu shows current synergy webs and future unlock hints.
- **Accessibility**: Colorblind palettes, remappable controls, damage number filters.

## Content Production Plan
- **Phase 1: Prototype (3 months)**
  - Implement core movement/combat, procedural room assembly, and modular weapon data-driven system.
  - Include 3 characters, 20 weapon modules, 15 relics, 2 biomes, and 1 boss.
- **Phase 2: Vertical Slice (6 months)**
  - Expand to 6 characters, 60 weapon modules, 40 relics, 3 bosses, full node map UI, and adaptive mutation prototype.
  - Conduct playtests to validate run variety metrics.
- **Phase 3: Content Ramp (6-8 months)**
  - Scale to target content counts: 12 characters, 120+ modules, 90 relics, 6 biomes, 12 minibosses, 6 bosses.
  - Integrate faction reputation, daily modifiers, and meta progression.

## Metrics & Telemetry Goals
- Track weapon module pick rates, win rates per character, and synergy combos leading to extreme outcomes.
- Monitor average run length, damage sources, and death causes to maintain fairness perception.
- Use heatmaps for room design iteration.

## Differentiators Summary
- **Module Fusion Crafting** ensures player agency within randomness.
- **Adaptive Enemy Mutations** keep builds in check without feeling unfair.
- **Narrative Faction System** ties meta choices to moment-to-moment gameplay.
- **Permutation Tracking** surfaces run uniqueness via end-screen breakdown of combos achieved vs global percentages.

## Next Steps
1. Build core prototype focusing on combat feel and module system.
2. Develop design tools for weapon/relic authoring with tagging for synergy detection.
3. Flesh out faction storylines and integrate into run modifiers.
4. Plan usability testing loops specifically targeting readability and decision load.
