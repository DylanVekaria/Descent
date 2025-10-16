from __future__ import annotations

"""Meta-progression utilities for Descent.

This module handles persistence of player currency, per-character upgrades,
global settings, achievement tracking, and the stat adjustments that are
applied when a run starts. It is intentionally lightweight so it functions on
future Python versions without extra dependencies. Save data is stored in the
user's home directory as a JSON file named ``.descent_progress.json``.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Mapping, MutableMapping, Tuple

from .character_data import CharacterProfile
from .constants import COLOR_PALETTES, DIFFICULTY_PRESETS


SAVE_PATH = Path.home() / ".descent_progress.json"


@dataclass
class SettingsState:
    """Player-configurable runtime options that persist between sessions."""

    master_volume: float = 0.7
    music_volume: float = 0.6
    sfx_volume: float = 0.8
    difficulty: str = "normal"
    screen_shake: bool = True
    damage_numbers: bool = True
    auto_pause: bool = True
    color_profile: str = "deep_ocean"
    show_tutorials: bool = True

    def clamp(self) -> None:
        self.master_volume = max(0.0, min(1.0, float(self.master_volume)))
        self.music_volume = max(0.0, min(1.0, float(self.music_volume)))
        self.sfx_volume = max(0.0, min(1.0, float(self.sfx_volume)))
        if self.difficulty not in DIFFICULTY_PRESETS:
            self.difficulty = "normal"
        if self.color_profile not in COLOR_PALETTES:
            self.color_profile = "deep_ocean"

    def to_dict(self) -> Dict[str, object]:
        return {
            "master_volume": self.master_volume,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "difficulty": self.difficulty,
            "screen_shake": self.screen_shake,
            "damage_numbers": self.damage_numbers,
            "auto_pause": self.auto_pause,
            "color_profile": self.color_profile,
            "show_tutorials": self.show_tutorials,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "SettingsState":
        state = cls()
        for key in state.to_dict().keys():
            if key in data:
                setattr(state, key, data[key])
        state.clamp()
        return state


@dataclass
class AchievementRecord:
    """Metadata for a tracked achievement."""

    unlocked: bool = False
    timestamp: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {"unlocked": self.unlocked, "timestamp": self.timestamp}

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "AchievementRecord":
        unlocked = bool(data.get("unlocked", False))
        timestamp = str(data.get("timestamp", ""))
        return cls(unlocked=unlocked, timestamp=timestamp)


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
    "bulwark": UpgradeDefinition(
        label="Bulwark Plating",
        stat="shield",
        per_level=18,
        costs=(150, 210, 280, 360, 460, 580),
        max_level=6,
        description="Adds a persistent energy shield at run start for this diver.",
    ),
    "scavenger": UpgradeDefinition(
        label="Scavenger Protocol",
        stat="drop_bonus",
        per_level=0.04,
        costs=(130, 180, 240, 320, 420),
        max_level=5,
        description="Increases the odds of extra loot drops during runs.",
    ),
    "windfall": UpgradeDefinition(
        label="Windfall Conduits",
        stat="bonus_credits",
        per_level=4,
        costs=(160, 220, 300, 390),
        max_level=4,
        description="Earn bonus Aether whenever a run concludes.",
    ),
    "archives": UpgradeDefinition(
        label="Archives Vault",
        stat="starting_relics",
        per_level=1,
        costs=(240, 360, 520),
        max_level=3,
        description="Begin expeditions with attuned relics from the Dive Lab archives.",
    ),
}


STAT_DEFAULTS: Dict[str, float] = {
    "runs_played": 0,
    "total_kills": 0,
    "total_damage_dealt": 0.0,
    "total_damage_taken": 0.0,
    "relics_bound": 0,
    "weapons_synced": 0,
    "upgrades_purchased": 0,
    "credits_earned": 0,
    "highest_combo": 0,
    "longest_run": 0.0,
    "deepest_stage": 0,
    "achievements_unlocked": 0,
    "abilities_used": 0,
}

BEST_STATS = {"highest_combo", "longest_run", "deepest_stage"}


@dataclass
class ProgressState:
    credits: int = 0
    purchased: Dict[str, Dict[str, int]] = field(default_factory=dict)
    achievements: Dict[str, AchievementRecord] = field(default_factory=dict)
    statistics: Dict[str, float] = field(default_factory=dict)
    unlocks: Dict[str, bool] = field(default_factory=dict)
    settings: SettingsState = field(default_factory=SettingsState)

    def ensure_character(self, characters: Iterable[CharacterProfile]) -> None:
        for character in characters:
            self.purchased.setdefault(character.name, {})

    def ensure_achievements(self) -> None:
        from .achievements import ACHIEVEMENTS

        for key in ACHIEVEMENTS:
            self.achievements.setdefault(key, AchievementRecord())

    def ensure_statistics(self) -> None:
        for key, default in STAT_DEFAULTS.items():
            self.statistics.setdefault(key, default)

    def to_dict(self) -> Dict[str, object]:
        return {
            "credits": self.credits,
            "purchased": self.purchased,
            "achievements": {key: record.to_dict() for key, record in self.achievements.items()},
            "statistics": self.statistics,
            "unlocks": self.unlocks,
            "settings": self.settings.to_dict(),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "ProgressState":
        credits = int(data.get("credits", 0))
        purchased: Dict[str, Dict[str, int]] = {}
        raw_purchased = data.get("purchased", {})
        if isinstance(raw_purchased, Mapping):
            for char, upgrades in raw_purchased.items():
                if isinstance(upgrades, Mapping):
                    purchased[char] = {k: int(v) for k, v in upgrades.items() if k in UPGRADE_DEFINITIONS}

        achievements: Dict[str, AchievementRecord] = {}
        raw_achievements = data.get("achievements", {})
        if isinstance(raw_achievements, Mapping):
            for key, record in raw_achievements.items():
                if isinstance(record, Mapping):
                    achievements[key] = AchievementRecord.from_mapping(record)

        statistics: Dict[str, float] = {}
        raw_stats = data.get("statistics", {})
        if isinstance(raw_stats, Mapping):
            for key, value in raw_stats.items():
                try:
                    statistics[key] = float(value)
                except (TypeError, ValueError):
                    continue

        unlocks: Dict[str, bool] = {}
        raw_unlocks = data.get("unlocks", {})
        if isinstance(raw_unlocks, Mapping):
            for key, value in raw_unlocks.items():
                unlocks[key] = bool(value)

        settings_data = data.get("settings", {})
        if isinstance(settings_data, Mapping):
            settings = SettingsState.from_mapping(settings_data)
        else:
            settings = SettingsState()

        state = cls(
            credits=credits,
            purchased=purchased,
            achievements=achievements,
            statistics=statistics,
            unlocks=unlocks,
            settings=settings,
        )
        state.ensure_statistics()
        return state


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
    state.ensure_statistics()
    state.ensure_achievements()
    return state


def save_progress(state: ProgressState) -> None:
    """Persist the player's progress to disk."""

    try:
        SAVE_PATH.write_text(json.dumps(state.to_dict(), indent=2))
    except OSError:
        # Failing to write the save file should not crash the game.
        pass


def update_settings(state: ProgressState, key: str, value: object) -> None:
    """Update a settings attribute and persist the progress file."""

    if hasattr(state.settings, key):
        setattr(state.settings, key, value)
        state.settings.clamp()
        save_progress(state)


def record_statistics(state: ProgressState, updates: Mapping[str, float]) -> None:
    """Accumulate statistics in the persistent profile."""

    state.ensure_statistics()
    for key, value in updates.items():
        if key in BEST_STATS:
            state.statistics[key] = max(state.statistics.get(key, 0), float(value))
        else:
            state.statistics[key] = state.statistics.get(key, 0) + float(value)


def count_unlocked(state: ProgressState) -> int:
    return sum(1 for record in state.achievements.values() if record.unlocked)


def record_run(state: ProgressState, run_stats: Mapping[str, float]) -> list["AchievementDefinition"]:
    """Apply a run summary to persistent stats and unlock achievements."""

    from .achievements import ACHIEVEMENTS

    record_statistics(
        state,
        {
            "runs_played": 1,
            "total_kills": run_stats.get("kills", 0),
            "total_damage_dealt": run_stats.get("damage_dealt", 0.0),
            "total_damage_taken": run_stats.get("damage_taken", 0.0),
            "relics_bound": run_stats.get("relics", 0),
            "weapons_synced": run_stats.get("weapons", 0),
            "abilities_used": run_stats.get("ability_uses", 0),
            "credits_earned": run_stats.get("credits", 0),
        },
    )
    record_statistics(
        state,
        {
            "highest_combo": run_stats.get("combo", 0),
            "longest_run": run_stats.get("duration", 0.0),
            "deepest_stage": run_stats.get("stage", 0),
        },
    )

    unlocked: list["AchievementDefinition"] = []
    totals = state.statistics
    now = datetime.utcnow().isoformat()
    for key, definition in ACHIEVEMENTS.items():
        record = state.achievements.get(key)
        if record is None:
            record = AchievementRecord()
            state.achievements[key] = record
        if record.unlocked:
            continue
        if definition.is_met(run_stats, totals, state):
            record.unlocked = True
            record.timestamp = now
            if definition.reward_credits:
                state.credits += definition.reward_credits
                record_statistics(state, {"credits_earned": definition.reward_credits})
            unlocked.append(definition)

    state.ensure_statistics()
    state.statistics["achievements_unlocked"] = float(count_unlocked(state))
    save_progress(state)
    return unlocked


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
    record_statistics(state, {"upgrades_purchased": 1})
    save_progress(state)
    return True, f"Purchased {definition.label} Lv.{level + 1}!"


def award_credits(state: ProgressState, amount: int) -> None:
    state.credits += max(0, amount)
    if amount > 0:
        record_statistics(state, {"credits_earned": amount})
    save_progress(state)

