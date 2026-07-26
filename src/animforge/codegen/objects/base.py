from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ObjectCodeGenerator(ABC):
    """
    Base interface for generating Manim code
    for a single AnimForge scene object.
    """

    @property
    @abstractmethod
    def object_type(self) -> str:
        """
        Return the AnimForge object type.

        Examples:
            text
            circle
            rectangle
            arrow
        """
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        obj: Any,
        variable_name: str,
        variable_map: dict[str, str],
    ) -> list[str]:
        """
        Generate Manim Python source code.

        Args:
            obj:
                AnimForge scene object.

            variable_name:
                Python variable name assigned to
                the generated Manim object.

            variable_map:
                Mapping from AnimForge object IDs
                to generated Python variable names.

        Returns:
            List of Python source code lines.
        """
        raise NotImplementedError