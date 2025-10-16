from __future__ import annotations

from typing import Dict, Sequence, Tuple

import pygame

Color = Tuple[int, int, int]

# Each sprite is defined by rows of characters. Palette maps characters to RGBA colors.
# "_" denotes transparency.

PLAYER_PIXEL_MAP: Sequence[str] = [
    "____YYY_____",
    "___YWWWY____",
    "__YWWWWWY___",
    "__YWWWWWY___",
    "_YWBBBBBWY__",
    "_YWBKKKBWY__",
    "YWBKKKKKBWY_",
    "YWBKKKKKBWY_",
    "YWBKKKKKBWY_",
    "_YWBKKKBWY__",
    "_YWBBBBBWY__",
    "__YWWWWWY___",
    "__YWWWWWY___",
    "___YWWWY____",
    "____YYY_____",
]

ENEMY_PIXEL_MAPS: Dict[str, Sequence[str]] = {
    "wraith": [
        "____RRR____",
        "___RXXXR___",
        "__RXXXXXR__",
        "_RXXRRXXR_",
        "_RXXXXXXR_",
        "RXXXXXXXXR",
        "RXXRRRRXXR",
        "RXXXXXXXXR",
        "_RXXXXXXR_",
        "_RXXRRXXR_",
        "__RXXXXXR__",
        "___RXXXR___",
        "____RRR____",
    ],
    "cultist": [
        "____PPP____",
        "___PSSSP___",
        "__PSSSSSP__",
        "_PSSPPSSP_",
        "_PSSSSSSP_",
        "PSSSLLSSSP",
        "PSSLLLLSSP",
        "PSSSLLSSSP",
        "_PSSSSSSP_",
        "_PSSPPSSP_",
        "__PSSSSSP__",
        "___PSSSP___",
        "____PPP____",
    ],
    "golem": [
        "____MMM____",
        "___MNNNM___",
        "__MNNNNNM__",
        "_MNNMMMMNM_",
        "_MNNNNNNM_",
        "MNNNNNNNNM",
        "MNNMMMMNNM",
        "MNNNNNNNNM",
        "_MNNNNNNM_",
        "_MNNMMMMM_",
        "__MNNNNNM__",
        "___MNNNM___",
        "____MMM____",
    ],
}

PROJECTILE_PIXEL_MAP: Sequence[str] = [
    "__GG__",
    "_GFFG_",
    "GFFFFG",
    "_GFFG_",
    "__GG__",
]

PICKUP_PIXEL_MAP: Sequence[str] = [
    "__LLLL__",
    "_LDDDDL_",
    "LDDDDDDL",
    "LDDSSDDL",
    "LDDSSDDL",
    "LDDDDDDL",
    "_LDDDDL_",
    "__LLLL__",
]

PALETTES: Dict[str, Dict[str, Color]] = {
    "player": {
        "Y": (0, 0, 0, 0),  # placeholder replaced dynamically
        "W": (255, 255, 255, 255),
        "B": (64, 64, 80, 255),
        "K": (24, 24, 32, 255),
    },
    "wraith": {
        "R": (150, 54, 114, 255),
        "X": (255, 129, 170, 255),
    },
    "cultist": {
        "P": (120, 86, 142, 255),
        "S": (244, 182, 215, 255),
        "L": (244, 236, 202, 255),
    },
    "golem": {
        "M": (120, 108, 95, 255),
        "N": (194, 178, 128, 255),
    },
    "projectile": {
        "G": (255, 255, 255, 100),
        "F": (255, 208, 96, 255),
    },
    "pickup": {
        "L": (186, 255, 201, 255),
        "D": (74, 157, 107, 255),
        "S": (255, 255, 255, 255),
    },
}


def make_surface_from_map(
    pixel_map: Sequence[str],
    palette: Dict[str, Color],
    scale: int = 4,
    tint: Color | None = None,
) -> pygame.Surface:
    """Convert a pixel map to a pygame Surface."""

    width = len(pixel_map[0])
    height = len(pixel_map)
    surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)

    for y, row in enumerate(pixel_map):
        for x, key in enumerate(row):
            if key == "_":
                continue
            color = palette.get(key)
            if color is None:
                raise KeyError(f"Unknown color key '{key}' for palette")
            if tint is not None:
                # Blend tint with color
                tr, tg, tb = tint
                cr, cg, cb, *_ = color
                color = (
                    min(255, int((cr * 0.4) + (tr * 0.6))),
                    min(255, int((cg * 0.4) + (tg * 0.6))),
                    min(255, int((cb * 0.4) + (tb * 0.6))),
                    color[3],
                )
            surface.set_at((x, y), color)

    surface = pygame.transform.scale(surface, (width * scale, height * scale))
    return surface.convert_alpha()


def player_sprite(primary: Color, secondary: Color) -> pygame.Surface:
    palette = {
        "Y": (*primary, 255),
        "W": (*secondary, 255),
        "B": (64, 64, 80, 255),
        "K": (24, 24, 32, 255),
    }
    return make_surface_from_map(PLAYER_PIXEL_MAP, palette)


def enemy_sprite(enemy_key: str) -> pygame.Surface:
    pixel_map = ENEMY_PIXEL_MAPS[enemy_key]
    palette = PALETTES[enemy_key]
    return make_surface_from_map(pixel_map, palette)


def projectile_sprite(color: Color) -> pygame.Surface:
    palette = {
        "G": (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40), 120),
        "F": (*color, 255),
    }
    return make_surface_from_map(PROJECTILE_PIXEL_MAP, palette, scale=3)


def pickup_sprite(color: Color) -> pygame.Surface:
    palette = {
        "L": color + (255,),
        "D": (max(0, color[0] - 60), max(0, color[1] - 60), max(0, color[2] - 60), 255),
        "S": (255, 255, 255, 255),
    }
    return make_surface_from_map(PICKUP_PIXEL_MAP, palette, scale=3)

