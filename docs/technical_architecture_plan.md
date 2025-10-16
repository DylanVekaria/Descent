# Technical Architecture Plan

## Engine & Tools
- **Engine Choice**: Godot 4.x (C#) or Unity (URP) both viable. Recommend Godot for permissive licensing and 2D pipeline, but maintain abstraction to allow engine swap.
- **Language Stack**: Core gameplay in C# (Godot Mono) or GDScript for quick iteration. Data definitions in JSON/TSV with custom editor tools.
- **Version Control**: Git with LFS for large assets. Adopt trunk-based development with feature branches and gated CI.
- **CI/CD**: Automated builds per platform, linting for scripts, unit tests for gameplay math, static data validation.

## Modular Data-Driven Content
- **Weapon Data Schema**
  ```json
  {
    "id": "volt_lance",
    "frame": "spear",
    "base_stats": { "damage": 18, "fire_rate": 1.6, "crit": 0.12 },
    "modules": ["chain_fork", "overcharge"],
    "infusion_tags": ["volt"],
    "scaling": { "focus": 0.4, "flux": 0.2 }
  }
  ```
- Use tag-driven matching to surface synergies and ensure loot drops align with player build.
- Implement Google Sheets → CSV pipeline feeding importer scripts for fast iteration.

## Procedural Generation Framework
1. **Macro Layer (Node Graph)**
   - Weighted random algorithm ensuring path diversity.
   - Difficulty budget ensures tough encounters spaced evenly.
   - Events seeded with run ID for reproducibility.
2. **Room Assembly**
   - Tilemap chunks with sockets; algorithm selects chunk sets based on biome + challenge rating.
   - Hazard/cover placements influenced by player's mobility stat to maintain fairness.
3. **Encounter Director**
   - Maintains threat score based on enemy types, statuses, environmental hazards.
   - Adjust spawn waves dynamically to avoid spikes.

## Combat Systems
- **Stat Pipeline**: Base stats → character modifiers → relic buffs → temporary effects. Maintain order for predictability.
- **Damage Types**: Physical, Pyre, Frost, Volt, Void, Terra. Resistances per enemy.
- **Status Effects**:
  - *Pyre*: Burn DoT, stacks increase duration.
  - *Frost*: Slow, at 100 stacks freezes.
  - *Volt*: Chain lightning proc chance scaling with Focus.
  - *Void*: Apply vulnerability; kills spawn singularities.
  - *Terra*: Root/armor shred hybrid.
- **Hit Resolution**: Event-driven to allow on-hit modifiers and triggered abilities.
- **Aim Assist**: Optional toggles to support accessibility with predictive smoothing.

## AI Architecture
- **Behavior Trees** per enemy archetype with shared blackboard data for coordination.
- **Utility Scoring** for selecting abilities, factoring player distance, line of sight, statuses.
- **Telegraph System**: All major attacks emit warnings (UI overlay, audio cue) before execution.

## Meta-Progression Systems
- **Unlock Manager**: Central service gating content based on flags.
- **Faction Reputation**: Persistent data structure storing ranks, influences encounter seeds.
- **Daily Challenge Service**: Rotating seed schedule, server-authoritative for leaderboards.

## Tooling & Pipeline
- **Content Editor**: In-engine tool to edit modules/relics with validation rules (e.g., synergy tags required, cost budgets).
- **Simulation Suite**: Automated run simulator to test balance by running thousands of AI-driven runs overnight.
- **Telemetry Hooks**: Use open-source analytics (GameAnalytics) capturing build choices and run outcomes.

## Multiplayer/Live Features (Stretch)
- **Asynchronous Integration**: Ghost runs, leaderboard replays.
- **Co-op**: Potential future addition; design netcode abstraction early if feasible.

## Risk Management
- Establish performance budgets early (draw calls, particles) to maintain 60 FPS on mid-tier hardware.
- Build debug overlay for frame time, GC spikes, and event logging.
- Ensure deterministic seeds to assist QA reproduction.
