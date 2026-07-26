from __future__ import annotations

from typing import Any

from animforge.codegen.objects.base import (
    ObjectCodeGenerator,
)


class TextObjectCodeGenerator(
    ObjectCodeGenerator
):
    """
    Generate Manim code for AnimForge text objects.
    """

    @property
    def object_type(self) -> str:
        """
        Return the supported object type.
        """

        return "text"

    def generate(
        self,
        obj: Any,
        variable_name: str,
        variable_map: dict[str, str],
    ) -> list[str]:
        """
        Generate Manim Text object code.
        """

        content = obj.content or ""

        lines = [
            (
                f"{variable_name} = "
                f"Text({content!r})"
            ),
        ]

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
    def _generate_position(
        variable_name: str,
        obj: Any,
    ) -> list[str]:
        """
        Generate absolute position code.
        """

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

        position = obj.position

        if hasattr(
            position,
            "value",
        ):
            position = position.value

        position = str(
            position
        ).lower()

        if position in position_map:
            return [
                position_map[position]
            ]

        return []

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

        target_id = (
            relative.target
        )

        target_variable = (
            variable_map.get(
                target_id
            )
        )

        if target_variable is None:
            raise ValueError(
                "Relative position references "
                f"unknown object '{target_id}'."
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