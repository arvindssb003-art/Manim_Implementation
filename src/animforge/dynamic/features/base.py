from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DynamicFeature(ABC):
    """
    Base contract for dynamically discovered AnimForge features.

    A dynamic feature owns:
        - its command name
        - parsing its command
        - generating its Manim code

    New features should normally be implemented in one file
    by subclassing this class.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the command name handled by this feature.

        Example:

            return "graph"
        """

        raise NotImplementedError

    @abstractmethod
    def parse(
        self,
        line: str,
    ) -> Any:
        """
        Parse one command line into a feature-specific object.
        """

        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        obj: Any,
    ) -> list[str]:
        """
        Generate Manim Python code for a parsed feature object.
        """

        raise NotImplementedError