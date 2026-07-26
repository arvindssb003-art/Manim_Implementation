from __future__ import annotations

import re
from dataclasses import dataclass

from ..feature import DynamicFeature


@dataclass(frozen=True)
class GraphDefinition:
    """
    Definition of a dynamic graph object.
    """

    object_id: str
    expression: str
    color: str
    relation: str
    target: str


def parse_graph(
    line: str,
) -> GraphDefinition:
    """
    Parse a GRAPH command.

    Supported forms:

        GRAPH parabola: blue y=x^2 at center

        GRAPH parabola: blue expression=x^2 at center

        GRAPH line: red y=2*x+1 below title

        GRAPH curve: green expression=sin(x) right_of label
    """

    line = line.strip()

    # ---------------------------------------------------------
    # Extract:
    #
    # GRAPH <id>: <rest>
    # ---------------------------------------------------------

    header = re.fullmatch(
        r"GRAPH\s+"
        r"(?P<object_id>[A-Za-z_]\w*)"
        r"\s*:\s*"
        r"(?P<rest>.+)",
        line,
        flags=re.IGNORECASE,
    )

    if not header:
        raise ValueError(
            "Invalid GRAPH syntax. "
            "Expected: "
            "GRAPH <id>: <color> "
            "[expression=]<expression> "
            "at|below|above|left_of|right_of "
            "<target>."
        )

    object_id = (
        header.group(
            "object_id"
        )
    )

    rest = (
        header.group(
            "rest"
        ).strip()
    )

    # ---------------------------------------------------------
    # Extract position clause from the END.
    #
    # Example:
    #
    #   blue y=2*x+1 at center
    #
    # becomes:
    #
    #   body     = "blue y=2*x+1"
    #   relation = "at"
    #   target   = "center"
    # ---------------------------------------------------------

    position = re.search(
        r"\s+"
        r"(?P<relation>"
        r"at|below|above|left_of|right_of"
        r")"
        r"\s+"
        r"(?P<target>[A-Za-z_]\w*)"
        r"\s*$",
        rest,
        flags=re.IGNORECASE,
    )

    if not position:
        raise ValueError(
            "Invalid GRAPH syntax. "
            "Missing position clause. "
            "Expected: "
            "at|below|above|left_of|right_of "
            "<target>."
        )

    relation = (
        position.group(
            "relation"
        ).lower()
    )

    target = (
        position.group(
            "target"
        )
    )

    body = (
        rest[
            :position.start()
        ].strip()
    )

    # ---------------------------------------------------------
    # Extract color from beginning.
    #
    # Example:
    #
    #   blue y=x^2
    #
    # color = blue
    # expression = y=x^2
    # ---------------------------------------------------------

    color_match = re.match(
        r"(?P<color>[A-Za-z_]\w*)"
        r"\s+"
        r"(?P<expression>.+)",
        body,
        flags=re.IGNORECASE,
    )

    if not color_match:
        raise ValueError(
            "Invalid GRAPH syntax. "
            "Missing color or expression."
        )

    color = (
        color_match.group(
            "color"
        ).lower()
    )

    expression = (
        color_match.group(
            "expression"
        ).strip()
    )

    # ---------------------------------------------------------
    # Optional expression= prefix.
    #
    # expression=x^2
    # becomes:
    #
    # x^2
    # ---------------------------------------------------------

    if expression.lower().startswith(
        "expression="
    ):
        expression = expression[
            len("expression="):
        ].strip()

    # ---------------------------------------------------------
    # Optional y= prefix.
    #
    # y=x^2
    # becomes:
    #
    # x^2
    # ---------------------------------------------------------

    if expression.lower().startswith(
        "y="
    ):
        expression = expression[
            len("y="):
        ].strip()

    if not expression:
        raise ValueError(
            "GRAPH expression cannot be empty."
        )

    return GraphDefinition(
        object_id=object_id,
        expression=expression,
        color=color,
        relation=relation,
        target=target,
    )


def generate_graph(
    obj: GraphDefinition,
) -> list[str]:
    """
    Generate Manim code for a dynamic graph.

    User-friendly mathematical expressions use:

        x^2

    Python requires:

        x**2

    Therefore '^' is converted to '**'.
    """

    variable = (
        f"{obj.object_id}_obj"
    )

    expression = (
        obj.expression.replace(
            "^",
            "**",
        )
    )

    return [
        (
            f"{variable} = FunctionGraph("
            f"lambda x: {expression}"
            ")"
        ),
        (
            f"{variable}.set_color("
            f"{obj.color.upper()}"
            ")"
        ),
        (
            f"{variable}.move_to("
            "ORIGIN)"
        ),
    ]


# -------------------------------------------------------------
# Dynamic feature registration
#
# DynamicFeatureDiscovery searches modules for DynamicFeature
# instances. This registration makes the GRAPH feature
# automatically discoverable by the dispatcher.
# -------------------------------------------------------------

GRAPH_FEATURE = DynamicFeature(
    name="graph",
    parser=parse_graph,
    generator=generate_graph,
)