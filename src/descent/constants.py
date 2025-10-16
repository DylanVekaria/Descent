from __future__ import annotations

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TARGET_FPS = 60

TILE_SIZE = 48
PLAYER_LAYER = 5
ENEMY_LAYER = 4
PROJECTILE_LAYER = 6
PICKUP_LAYER = 3
BACKGROUND_LAYER = 1
UI_LAYER = 10

COLOR_PALETTES = {
    "deep_ocean": {
        "void": (18, 16, 41),
        "floor": (34, 32, 52),
        "wall": (48, 49, 60),
        "ui_bg": (20, 20, 25),
        "ui_accent": (255, 208, 96),
        "player_core": (102, 255, 178),
        "player_secondary": (45, 197, 253),
        "danger": (255, 82, 82),
        "warning": (255, 184, 108),
        "calm": (111, 255, 233),
        "loot": (186, 255, 201),
        "relic": (204, 170, 255),
        "shield": (120, 200, 255),
        "cooldown": (255, 147, 79),
        "combo": (255, 220, 128),
        "field": (86, 140, 255),
    },
    "neon_flux": {
        "void": (14, 6, 28),
        "floor": (42, 12, 54),
        "wall": (84, 24, 108),
        "ui_bg": (26, 12, 38),
        "ui_accent": (102, 255, 230),
        "player_core": (255, 138, 76),
        "player_secondary": (255, 229, 76),
        "danger": (255, 71, 122),
        "warning": (255, 195, 0),
        "calm": (138, 255, 255),
        "loot": (186, 255, 121),
        "relic": (178, 102, 255),
        "shield": (76, 221, 255),
        "cooldown": (255, 99, 210),
        "combo": (255, 241, 118),
        "field": (76, 201, 240),
    },
    "crimson_void": {
        "void": (24, 6, 8),
        "floor": (48, 18, 24),
        "wall": (96, 24, 36),
        "ui_bg": (32, 14, 18),
        "ui_accent": (255, 160, 102),
        "player_core": (255, 236, 179),
        "player_secondary": (255, 82, 82),
        "danger": (255, 107, 107),
        "warning": (255, 177, 66),
        "calm": (255, 227, 227),
        "loot": (255, 220, 180),
        "relic": (231, 154, 255),
        "shield": (255, 179, 186),
        "cooldown": (255, 140, 66),
        "combo": (255, 206, 90),
        "field": (255, 130, 130),
    },
}


def get_palette(name: str) -> dict[str, tuple[int, int, int]]:
    """Return a copy of the named color palette."""

    return COLOR_PALETTES.get(name, COLOR_PALETTES["deep_ocean"]).copy()


RUN_COLORS = get_palette("deep_ocean")


DIFFICULTY_PRESETS = {
    "story": {"enemy_hp": 0.82, "enemy_damage": 0.8, "enemy_speed": 0.94, "spawn_rate": 0.85, "reward": 0.9},
    "normal": {"enemy_hp": 1.0, "enemy_damage": 1.0, "enemy_speed": 1.0, "spawn_rate": 1.0, "reward": 1.0},
    "veteran": {"enemy_hp": 1.18, "enemy_damage": 1.14, "enemy_speed": 1.06, "spawn_rate": 1.12, "reward": 1.15},
    "apocalypse": {"enemy_hp": 1.4, "enemy_damage": 1.32, "enemy_speed": 1.12, "spawn_rate": 1.22, "reward": 1.25},
}


FONT_PATH = None  # Use pygame default

