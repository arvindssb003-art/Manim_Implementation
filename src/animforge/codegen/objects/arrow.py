from __future__ import annotations

from typing import Any

from animforge.codegen.objects.base import (
    ObjectCodeGenerator,
)


class ArrowObjectCodeGenerator(
    ObjectCodeGenerator
):
    """
    Generate Manim code for AnimForge arrow objects.
    """

    @property
    def object_type(self) -> str:
        return "arrow"

    def generate(
        self,
        obj: Any,
        variable_name: str,
        variable_map: dict[str, str],
    ) -> list[str]:
        """
        Generate Manim Arrow object code.
        """

        if not obj.start:
            raise ValueError(
                f"Arrow '{obj.name}' "
                "is missing start reference."
            )

        if not obj.end:
            raise ValueError(
                f"Arrow '{obj.name}' "
                "is missing end reference."
            )

        start_variable = (
            variable_map.get(
                obj.start
            )
        )

        if start_variable is None:
            raise ValueError(
                f"Arrow '{obj.name}' "
                "references unknown start "
                f"object '{obj.start}'."
            )

        end_variable = (
            variable_map.get(
                obj.end
            )
        )

        if end_variable is None:
            raise ValueError(
                f"Arrow '{obj.name}' "
                "references unknown end "
                f"object '{obj.end}'."
            )

        return [
            (
                f"{variable_name} = Arrow("
                f"{start_variable}.get_center(), "
                f"{end_variable}.get_center()"
                f")"
            ),
        ]