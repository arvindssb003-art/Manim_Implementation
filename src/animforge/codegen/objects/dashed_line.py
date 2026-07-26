from __future__ import annotations

from animforge.codegen.objects.base import (
    ObjectCodeGenerator,
)
from animforge.models import (
    DashedLineObject,
    ObjectType,
)


class DashedLineObjectCodeGenerator(
    ObjectCodeGenerator
):
    """Generate Manim code for dashed lines."""

    @property
    def object_type(
        self,
    ) -> ObjectType:
        """Return the supported AnimForge object type."""

        return ObjectType.DASHED_LINE

    def generate(
        self,
        obj: DashedLineObject,
        variable_name: str,
        variable_map: dict[str, str],
    ) -> list[str]:
        """Generate code for a dashed line."""

        start = variable_map[
            obj.start
        ]

        end = variable_map[
            obj.end
        ]

        return [
            f"{variable_name} = DashedLine(",
            f"    {start}.get_center(),",
            f"    {end}.get_center(),",
            ")",
        ]