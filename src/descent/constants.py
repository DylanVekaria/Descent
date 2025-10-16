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

RUN_COLORS = {
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
}

FONT_PATH = None  # Use pygame default

