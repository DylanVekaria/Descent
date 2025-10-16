# Run Permutation Strategy

## Goals
- Ensure each run surfaces new combinations of weapons, modules, relics, and events.
- Provide player agency to steer randomness without reducing surprise.
- Track and celebrate unique permutations to reinforce replay value.

## Systems Enabling Variety

### 1. Content Taxonomy & Tagging
- **Tags**: Damage type, playstyle (melee, ranged, pet, control), resource usage, faction alignment.
- **Weighted Loot Tables**: Drop rates adjust based on underrepresented tags in the current build to push diversity.
- **Synergy Detection**: When player acquires items sharing tags, unlock special combo effects or branching upgrades.

### 2. Draft Nodes & Choice Architecture
- Offer 3–4 curated options per reward node, each from different archetype buckets.
- Allow limited rerolls (consuming Scrap) so players can pursue targeted strategies.
- Introduce "Glimpses"—previews of upcoming choices so players can plan route, increasing decision depth.

### 3. Adaptive Events
- Event deck seeded with triggers based on player's build metrics (e.g., high Volt usage unlocks electrical storms event).
- Faction reputation modifies available events, creating narrative variation between runs.
- Secret events require specific item combos, rewarding exploration of rare permutations.

### 4. Mutation Director
- Tracks player's dominant stats and modules, adjusts enemy modifiers accordingly.
- Mutations include resistances, attack patterns, environmental hazards, ensuring players pivot strategies mid-run.

### 5. Meta Progression Influence
- Unlocking new content expands loot pool but is gated to avoid dilution. New items initially appear in higher frequency to encourage testing.
- Daily modifiers temporarily adjust drop tables, encouraging experimentation with content otherwise underused.

## Permutation Tracking & Feedback
- **Run Summary Screen**: Displays unique combo identifiers (e.g., "Volt Tempest" combo achieved by combining Storm Lash module + Voltaic Sigil + Circuit Savant passive) with global rarity percentages.
- **Codex**: Catalog discovered synergies and hints at undiscovered ones via silhouettes.
- **Milestones**: Award achievements for discovering certain number of unique combos, encouraging broad experimentation.

## Balancing Considerations
- Ensure fail-safe builds exist (baseline effective combos) so variety does not hinder success.
- Regularly rotate content via patches; retire underperforming items temporarily for reworks.
- Monitor telemetry to detect degenerative combos; introduce soft counters rather than hard nerfs to preserve fun.

## Implementation Roadmap
1. Build tagging and loot weighting system in prototype.
2. Implement synergy detection logic and run summary UI.
3. Add mutation director hooks responding to build metrics.
4. Integrate faction/event dependencies and track player discovery progression.
