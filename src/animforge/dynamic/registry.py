from __future__ import annotations

from typing import Iterable

from .feature import DynamicFeature


class DynamicFeatureRegistry:
    """Registry for dynamically added AnimForge features."""

    def __init__(
        self,
        features: Iterable[DynamicFeature] | None = None,
    ) -> None:
        self._features: dict[
            str,
            DynamicFeature,
        ] = {}

        if features:
            for feature in features:
                self.register(feature)

    def register(
        self,
        feature: DynamicFeature,
    ) -> None:
        """Register a dynamic feature."""

        name = feature.name.strip().lower()

        if not name:
            raise ValueError(
                "Dynamic feature name cannot be empty."
            )

        if name in self._features:
            raise ValueError(
                f"Dynamic feature '{name}' "
                "is already registered."
            )

        self._features[name] = feature

    def get(
        self,
        name: str,
    ) -> DynamicFeature:
        """Retrieve a registered dynamic feature."""

        normalized = (
            name.strip().lower()
        )

        try:
            return self._features[
                normalized
            ]

        except KeyError as exc:
            raise ValueError(
                f"Unsupported dynamic feature: "
                f"'{name}'. "
                f"Supported features: "
                f"{sorted(self._features)}"
            ) from exc

    def has(
        self,
        name: str,
    ) -> bool:
        """Check whether a feature is registered."""

        return (
            name.strip().lower()
            in self._features
        )

    def all(
        self,
    ) -> list[DynamicFeature]:
        """Return all registered features."""

        return list(
            self._features.values()
        )