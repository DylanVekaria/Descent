# Descent Production Roadmap

This document expands on the high-level roadmap from the README with task-level detail so sprint planning can translate directly into implementation tickets. Dates refer to target quarters for the playable prototype.

## Q1 – Deepen the Core Loop

### Systems
- **Arena Module Pipeline** – Build a lightweight editor script that stitches together wall/hazard prefabs into JSON layouts consumed by the runtime arena loader.
- **Enemy Affix Framework** – Introduce mixins that apply stat modifiers, behavioral overrides, and VFX to base enemy archetypes (e.g., `Shielded`, `Warp-Touched`).
- **Audio Layering** – Wire up FMOD or pygame.mixer scenes with three music stems (calm, combat, climax) and event-based SFX triggers for weapon fire, hits, pickups, and UI.

### Content
- Author at least 12 arena layouts categorized by threat level and wave pacing.
- Draft three affix pools tuned to beginner, intermediate, and expert difficulty tiers.
- Source or compose 20+ SFX assets and 3 minute music loops compatible with dynamic layering.

## Q2 – Expand Meta and Progression

### Systems
- **Diver Questlines** – Script modular quest objectives (e.g., “Clear Stage 5 without damage”) that unlock new active abilities and cosmetics per diver.
- **Relic Forge** – Design a reroll table that consumes duplicate weapons to mint relics providing persistent modifiers, with UI flow integrated into the Dive Lab.
- **Weekly Dive Infrastructure** – Implement seed serialization and leaderboard posting endpoints (local JSON stub initially, ready for later backend swap).

### Content
- Produce narrative snippets and VO placeholders for each diver questline milestone.
- Create 30 relic perks aligned to weapon keyword families, ensuring synergy overlap across builds.
- Curate a rotation of 8 weekly modifiers (e.g., “Double enemy speed, half damage taken”) that refresh automatically.

## Q3 – Productionization & Platform Support

### Systems
- **Cloud Sync** – Abstract save IO behind a provider interface supporting local filesystem and future cloud providers.
- **Tutorialization** – Build guided scenarios with scripted prompts, ghost replays, and fail-state resets to teach advanced movement.
- **Deck Mode** – Add a configuration profile for Steam Deck including 1280x800 layout, controller bindings, and performance telemetry overlay.

### Content
- Commission or produce HD key art, store capsule imagery, and promotional motion clips.
- Translate UI strings into at least three target languages (FR, ES, JP) to validate localization pipeline.
- Conduct two rounds of external playtests focused on retention of the meta-progression loop and accessibility feedback.

## Q0 – Prototype Mega Update (Delivered)

### Systems
- ☑ **Signature Abilities** – Diver-specific actives, combo scaling, and cooldown UI implemented in prototype.
- ☑ **Relic Binding** – In-run relic drops, stat stacking, and Dive Lab upgrade hooks wired to persistence.
- ☑ **Dynamic Events** – Timed arena events (supply drops, relic caches, healing fields, stasis wells) integrated into the wave loop.
- ☑ **Support Drones** – Orbiting allies with AI targeting, relic synergies, and meta upgrade support.

### Content
- ☑ Authored 16 relic profiles covering offense, defense, economy, and combo-enhancing effects.
- ☑ Authored 12 signature abilities with bespoke tuning, payload data, and UI copy.
- ☑ Expanded HUD copy and documentation to surface new mechanics (combo tiers, ability prompts, relic catalog).

## Q4 – Systems Expansion & Live Ops Prep

### Systems
- **Ability Mastery Tracks** – Introduce per-ability mastery that unlocks modifiers (extra charges, alternative effects) through usage challenges.
- **Event Variant Deck** – Author additional arena events (ambush waves, hazard storms, drone beacons) with difficulty scaling knobs.
- **Relic Synergy Matrix** – Implement UI overlays and backend tracking that highlight combos between relic families and weapon keywords.
- **Automated Balancing Telemetry** – Pipe combo tier uptime, relic pick rates, and ability usage into analytics exports for balancing.

### Content
- Draft lore snippets and VO callouts triggered when abilities are activated at max combo tier.
- Create new relic families tied to elemental themes (Frost Bloom, Storm Engine) with escalating art variations.
- Design two mini-boss encounters that explicitly test the new systems (gravity immune juggernaut, drone jamming mage).

---

**Status Legend**

| Status | Meaning |
| ------ | ------- |
| ☐ | Not started |
| ◐ | In progress |
| ☑ | Complete |

> Progress updates should be appended per sprint with date stamps to keep the roadmap actionable.

