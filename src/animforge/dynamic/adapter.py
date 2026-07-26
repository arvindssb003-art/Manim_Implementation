from __future__ import annotations

from typing import Any

from .feature import DynamicFeature
from .registry import DynamicFeatureRegistry


class DynamicFeatureAdapter:
    """
    Adapter between the dynamic registry and feature modules.

    Supports dynamic feature registration, discovery,
    parsing, and code generation.
    """

    def __init__(
        self,
        registry: DynamicFeatureRegistry | None = None,
    ) -> None:
        self.registry = (
            registry
            or DynamicFeatureRegistry()
        )

    def register(
        self,
        feature: DynamicFeature,
    ) -> None:
        """
        Register a dynamic feature.
        """

        self.registry.register(
            feature
        )

    def has(
        self,
        name: str,
    ) -> bool:
        """
        Return whether a feature exists.
        """

        return self.registry.has(
            name
        )

    def get(
        self,
        name: str,
    ) -> DynamicFeature:
        """
        Get a registered feature.
        """

        return self.registry.get(
            name
        )

    def list_features(
        self,
    ) -> list[str]:
        """
        Return registered feature names.

        This intentionally reads the registry's internal
        feature mapping because older registry versions
        do not expose a list_features() method.
        """

        return sorted(
            self.registry._features.keys()
        )

    def parse(
        self,
        name: str,
        value: str,
    ) -> Any:
        """
        Parse a dynamic feature.

        Supports both full-line and payload-style
        feature parsers.
        """

        feature = self.get(
            name
        )

        try:
            return feature.parser(
                value
            )

        except ValueError as first_error:

            payload = self._remove_command(
                name,
                value,
            )

            if payload == value:
                raise

            try:
                return feature.parser(
                    payload
                )

            except ValueError:
                raise first_error

    def generate(
        self,
        name: str,
        value: Any,
    ) -> list[str]:
        """
        Generate code for a parsed feature.
        """

        feature = self.get(
            name
        )

        return feature.generator(
            value
        )

    @staticmethod
    def _remove_command(
        name: str,
        value: str,
    ) -> str:
        """
        Remove the command prefix from a full command line.

        Example:

            GRAPH parabola: blue y=x^2 at center

        becomes:

            parabola: blue y=x^2 at center
        """

        prefix = (
            name.strip()
            + " "
        )

        if value.lower().startswith(
            prefix.lower()
        ):
            return value[
                len(prefix):
            ].strip()

        return value