from __future__ import annotations

from typing import Any

from animforge.codegen.objects.base import (
    ObjectCodeGenerator,
)


class RoundedRectangleObjectCodeGenerator(
    ObjectCodeGenerator
):
    """
    Generate Manim code for AnimForge
    rounded rectangle objects.
    """

    @property
    def object_type(self) -> str:
        return "rounded_rectangle"

    def generate(
        self,
        obj: Any,
        variable_name: str,
        variable_map: dict[str, str],
    ) -> list[str]:
        """
        Generate Manim RoundedRectangle object code.
        """

        lines = [
            (
                f"{variable_name} = "
                f"RoundedRectangle("
                f"width={obj.width}, "
                f"height={obj.height}, "
                f"corner_radius={obj.corner_radius}"
                f")"
            ),
        ]

        if obj.color:
            lines.append(
                f"{variable_name}.set_color("
                f"{self._color_constant(obj.color)}"
                f")"
            )

        if obj.position:
            lines.extend(
                self._generate_position(
                    variable_name,
                    obj,
                )
            )

        elif obj.relative_position:
            lines.extend(
                self._generate_relative_position(
                    variable_name,
                    obj,
                    variable_map,
                )
            )

        return lines

    @staticmethod
    def _color_constant(
        color: str,
    ) -> str:
        """
        Convert a color name to a Manim constant.
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

        return color_map.get(
            color.lower(),
            "WHITE",
        )

    @staticmethod
    def _generate_position(
        variable_name: str,
        obj: Any,
    ) -> list[str]:
        """
        Generate absolute position code.
        """

        position = obj.position

        if hasattr(
            position,
            "value",
        ):
            position = position.value

        position_map = {
            "center": (
                f"{variable_name}.move_to(ORIGIN)"
            ),
            "top": (
                f"{variable_name}.to_edge(UP)"
            ),
            "bottom": (
                f"{variable_name}.to_edge(DOWN)"
            ),
            "left": (
                f"{variable_name}.to_edge(LEFT)"
            ),
            "right": (
                f"{variable_name}.to_edge(RIGHT)"
            ),
            "top_left": (
                f"{variable_name}.to_corner(UL)"
            ),
            "top_right": (
                f"{variable_name}.to_corner(UR)"
            ),
            "bottom_left": (
                f"{variable_name}.to_corner(DL)"
            ),
            "bottom_right": (
                f"{variable_name}.to_corner(DR)"
            ),
        }

        line = position_map.get(
            str(position).lower()
        )

        return [line] if line else []

    @staticmethod
    def _generate_relative_position(
        variable_name: str,
        obj: Any,
        variable_map: dict[str, str],
    ) -> list[str]:
        """
        Generate relative position code.
        """

        relative = (
            obj.relative_position
        )

        target_variable = (
            variable_map.get(
                relative.target
            )
        )

        if target_variable is None:
            raise ValueError(
                "Relative position references "
                f"unknown object "
                f"'{relative.target}'."
            )

        relation = (
            relative.relation
        )

        if hasattr(
            relation,
            "value",
        ):
            relation = relation.value

        direction_map = {
            "below": "DOWN",
            "above": "UP",
            "left_of": "LEFT",
            "right_of": "RIGHT",
        }

        direction = direction_map.get(
            str(relation).lower()
        )

        if direction is None:
            raise ValueError(
                "Unsupported relative position: "
                f"'{relation}'."
            )

        return [
            (
                f"{variable_name}.next_to("
                f"{target_variable}, "
                f"{direction}"
                f")"
            ),
        ]