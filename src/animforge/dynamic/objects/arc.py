from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from animforge.dynamic import DynamicFeature


@dataclass(frozen=True)
class ArcDefinition:
    """Definition of a dynamically parsed arc."""

    object_id: str
    color: str
    radius: float
    start_angle: float
    angle: float
    position: str


def parse_arc(
    value: str,
) -> ArcDefinition:
    """
    Parse a dynamic ARC definition.

    Expected format:

        arc_id: color radius=<r> start=<angle> angle=<angle> at <position>

    Example:

        arc1: red radius=2 start=0 angle=180 at center
    """

    import re

    match = re.fullmatch(
        r"(\w+):\s*(\w+)"
        r"(?:\s+radius=(\d+(?:\.\d+)?))?"
        r"(?:\s+start=(-?\d+(?:\.\d+)?))?"
        r"(?:\s+angle=(-?\d+(?:\.\d+)?))?"
        r"\s+at\s+(\w+)",
        value.strip(),
        flags=re.IGNORECASE,
    )

    if not match:
        raise ValueError(
            "Invalid ARC syntax. Expected: "
            "ARC <id>: <color> "
            "[radius=<r>] "
            "[start=<angle>] "
            "[angle=<angle>] "
            "at <position>."
        )

    (
        object_id,
        color,
        radius,
        start_angle,
        angle,
        position,
    ) = match.groups()

    radius_value = (
        float(radius)
        if radius is not None
        else 1.0
    )

    start_angle_value = (
        float(start_angle)
        if start_angle is not None
        else 0.0
    )

    angle_value = (
        float(angle)
        if angle is not None
        else 90.0
    )

    if radius_value <= 0:
        raise ValueError(
            "ARC radius must be greater than 0."
        )

    return ArcDefinition(
        object_id=object_id,
        color=color.lower(),
        radius=radius_value,
        start_angle=start_angle_value,
        angle=angle_value,
        position=position.lower(),
    )


def generate_arc(
    definition: ArcDefinition,
) -> list[str]:
    """
    Generate Manim code for a dynamic ARC.
    """

    color_map = {
        "red": "RED",
        "blue": "BLUE",
        "green": "GREEN",
        "yellow": "YELLOW",
        "orange": "ORANGE",
        "purple": "PURPLE",
        "pink": "PINK",
        "white": "WHITE",
        "black": "BLACK",
    }

    color = color_map.get(
        definition.color,
        "WHITE",
    )

    variable = (
        f"{definition.object_id}_obj"
    )

    lines = [
        (
            f"{variable} = Arc("
            f"radius={definition.radius}, "
            f"start_angle="
            f"{definition.start_angle}, "
            f"angle="
            f"{definition.angle}"
            f")"
        ),
        f"{variable}.set_color({color})",
    ]

    position_map = {
        "center": (
            f"{variable}.move_to(ORIGIN)"
        ),
        "top": (
            f"{variable}.to_edge(UP)"
        ),
        "bottom": (
            f"{variable}.to_edge(DOWN)"
        ),
        "left": (
            f"{variable}.to_edge(LEFT)"
        ),
        "right": (
            f"{variable}.to_edge(RIGHT)"
        ),
    }

    position_line = position_map.get(
        definition.position
    )

    if position_line is None:
        raise ValueError(
            f"Unsupported ARC position: "
            f"'{definition.position}'."
        )

    lines.append(
        position_line
    )

    return lines


ARC_FEATURE = DynamicFeature(
    name="arc",
    parser=parse_arc,
    generator=generate_arc,
)