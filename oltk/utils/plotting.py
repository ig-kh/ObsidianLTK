from enum import Enum
from typing import TypeAlias
from typing import Literal, TypeAlias


class GEM_PALETTE(Enum):
    obsidian = (
        (int("E8", 16), int("D9", 16), int("FF", 16)),
        (int("4B", 16), int("00", 16), int("82", 16)),
    )
    ruby = (
        (int("FF", 16), int("99", 16), int("99", 16)),
        (int("8B", 16), int("00", 16), int("33", 16)),
    )
    saphire = (
        (int("CC", 16), int("E5", 16), int("FF", 16)),
        (int("00", 16), int("33", 16), int("66", 16)),
    )
    emerald = (
        (int("99", 16), int("FF", 16), int("CC", 16)),
        (int("00", 16), int("66", 16), int("33", 16)),
    )


GemColor: TypeAlias = Literal["obsidian", "ruby", "saphire", "emerald"]


def generate_color_lin_scale(n_points: int, color: GemColor = "obsidian"):
    colors = []

    (r1, g1, b1), (r2, g2, b2) = GEM_PALETTE[color].value

    for i in range(n_points):
        t = i / (n_points - 1)

        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        colors.append(hex_color)

    return colors


def generate_color_lin_scale_with_fade(
    n_points: int,
    color: GemColor = "obsidian",
    min_alpha: float = 0.25,
    max_alpha: float = 0.95,
):
    colors = []

    (r1, g1, b1), (r2, g2, b2) = GEM_PALETTE[color].value

    for i in range(n_points):
        t = i / (n_points - 1)

        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        alpha = min_alpha + (max_alpha - min_alpha) * t

        rgba_color = f"rgba({r}, {g}, {b}, {alpha:.3f})"
        colors.append(rgba_color)

    return colors
