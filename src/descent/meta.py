from __future__ import annotations

"""Meta-progression utilities for Descent.

This module handles persistence of player currency, per-character upgrades, and
the stat adjustments that are applied when a run starts. It is intentionally
lightweight so it functions on future Python versions without extra
dependencies. Save data is stored in the user's home directory as a JSON file
named ``.descent_progress.json``.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, Iterable, Mapping, MutableMapping, Tuple

from .character_data import CharacterProfile


SAVE_PATH = Path.home() / ".descent_progress.json"


@dataclass
class UpgradeDefinition:
    """Configuration for a single upgrade track."""

    label: str
    stat: str
    per_level: float
    costs: Tuple[int, ...]
    max_level: int
    description: str

    def cost_for_level(self, current_level: int) -> int:
        if current_level >= self.max_level:
            return 0
        if current_level < len(self.costs):
            return self.costs[current_level]
        return self.costs[-1]


UPGRADE_DEFINITIONS: Dict[str, UpgradeDefinition] = {
    "vitality": UpgradeDefinition(
        label="Vitality Matrix",
        stat="max_hp",
        per_level=12,
        costs=(120, 160, 220, 320, 420, 560, 720),
        max_level=10,
        description="Permanently increases maximum integrity for this diver.",
    ),
    "arsenal": UpgradeDefinition(
        label="Arsenal Calibration",
        stat="damage",
        per_level=0.07,
        costs=(140, 200, 260, 340, 450, 580, 760),
        max_level=8,
        description="Improves outgoing weapon damage multipliers.",
    ),
    "tempo": UpgradeDefinition(
        label="Tempo Overdrive",
        stat="speed",
        per_level=10,
        costs=(90, 140, 190, 260, 340, 440, 560, 700),
        max_level=10,
        description="Increases base movement speed, keeping runs fast and fluid.",
    ),
    "focus": UpgradeDefinition(
        label="Focus Harmonizer",
        stat="focus",
        per_level=0.08,
        costs=(110, 160, 220, 300, 390, 510, 660),
        max_level=9,
        description="Reduces reload times and buffs utility-focused weapons.",
    ),
}


@dataclass
class ProgressState:
    credits: int = 0
    purchased: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def ensure_character(self, characters: Iterable[CharacterProfile]) -> None:
        for character in characters:
            self.purchased.setdefault(character.name, {})

    def to_dict(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        return {"credits": self.credits, "purchased": self.purchased}

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "ProgressState":
        credits = int(data.get("credits", 0))
        purchased: Dict[str, Dict[str, int]] = {}
        raw_purchased = data.get("purchased", {})
        if isinstance(raw_purchased, Mapping):
            for char, upgrades in raw_purchased.items():
                if isinstance(upgrades, Mapping):
                    purchased[char] = {k: int(v) for k, v in upgrades.items() if k in UPGRADE_DEFINITIONS}
        return cls(credits=credits, purchased=purchased)


def load_progress(characters: Iterable[CharacterProfile]) -> ProgressState:
    """Load the persisted meta-progression file if it exists."""

    if SAVE_PATH.exists():
        try:
            data = json.loads(SAVE_PATH.read_text())
            state = ProgressState.from_mapping(data)
        except (json.JSONDecodeError, OSError):
            state = ProgressState()
    else:
        state = ProgressState()
    state.ensure_character(characters)
    return state


def save_progress(state: ProgressState) -> None:
    """Persist the player's progress to disk."""

    try:
        SAVE_PATH.write_text(json.dumps(state.to_dict(), indent=2))
    except OSError:
        # Failing to write the save file should not crash the game.
        pass


def apply_upgrades(character: CharacterProfile, progress: ProgressState) -> Dict[str, float]:
    """Return the upgraded stats for a given character."""

    stats = character.stats.copy()
    char_progress = progress.purchased.get(character.name, {})
    for key, definition in UPGRADE_DEFINITIONS.items():
        level = char_progress.get(key, 0)
        if level <= 0:
            continue
        stats[definition.stat] = stats.get(definition.stat, 0) + definition.per_level * level
    return stats


def upgrade_summary(character: CharacterProfile, progress: ProgressState) -> Dict[str, int]:
    """Return the number of levels for each upgrade track."""

    return progress.purchased.get(character.name, {}).copy()


def can_purchase_upgrade(state: ProgressState, character: CharacterProfile, upgrade_key: str) -> bool:
    definition = UPGRADE_DEFINITIONS[upgrade_key]
    level = state.purchased.get(character.name, {}).get(upgrade_key, 0)
    if level >= definition.max_level:
        return False
    return state.credits >= definition.cost_for_level(level)


def purchase_upgrade(state: ProgressState, character: CharacterProfile, upgrade_key: str) -> Tuple[bool, str]:
    """Attempt to purchase an upgrade for a character."""

    if upgrade_key not in UPGRADE_DEFINITIONS:
        return False, "Unknown upgrade." 

    definition = UPGRADE_DEFINITIONS[upgrade_key]
    char_upgrades: MutableMapping[str, int] = state.purchased.setdefault(character.name, {})
    level = char_upgrades.get(upgrade_key, 0)
    if level >= definition.max_level:
        return False, "Track maxed."
    cost = definition.cost_for_level(level)
    if state.credits < cost:
        return False, "Insufficient credits."
    state.credits -= cost
    char_upgrades[upgrade_key] = level + 1
    save_progress(state)
    return True, f"Purchased {definition.label} Lv.{level + 1}!"


def award_credits(state: ProgressState, amount: int) -> None:
    state.credits += max(0, amount)
    save_progress(state)

