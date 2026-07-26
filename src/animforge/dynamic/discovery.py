from __future__ import annotations

import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Iterable

from .feature import DynamicFeature


class DynamicFeatureDiscovery:
    """
    Discover dynamic AnimForge features automatically.

    Feature modules may live in either:

        animforge.dynamic.objects
        animforge.dynamic.features

    Any module containing one or more DynamicFeature
    instances will be discovered and registered.

    Adding a new dynamic feature should therefore require
    only adding a feature module.
    """

    DEFAULT_PACKAGES = (
        "animforge.dynamic.objects",
        "animforge.dynamic.features",
    )

    def __init__(
        self,
        package_names: Iterable[str] | None = None,
    ) -> None:
        """
        Initialize dynamic feature discovery.

        Args:
            package_names:
                Optional packages to scan.

                When omitted, both the legacy object package
                and the newer feature package are scanned.
        """

        self.package_names = tuple(
            package_names
            or self.DEFAULT_PACKAGES
        )

    def discover_modules(
        self,
    ) -> list[ModuleType]:
        """
        Discover and import all modules from all
        configured feature packages.
        """

        modules: list[ModuleType] = []

        seen: set[str] = set()

        for package_name in self.package_names:

            package = importlib.import_module(
                package_name
            )

            if not hasattr(
                package,
                "__path__",
            ):
                continue

            for module_info in pkgutil.iter_modules(
                package.__path__
            ):

                module_name = (
                    f"{package_name}."
                    f"{module_info.name}"
                )

                if module_name in seen:
                    continue

                seen.add(
                    module_name
                )

                modules.append(
                    importlib.import_module(
                        module_name
                    )
                )

        return modules

    @staticmethod
    def discover_features(
        modules: Iterable[ModuleType],
    ) -> list[DynamicFeature]:
        """
        Find DynamicFeature instances in imported modules.
        """

        features: list[
            DynamicFeature
        ] = []

        seen: set[str] = set()

        for module in modules:

            for _, value in inspect.getmembers(
                module
            ):

                if not isinstance(
                    value,
                    DynamicFeature,
                ):
                    continue

                # Avoid duplicate registration if the same
                # feature object is imported into multiple modules.
                if value.name in seen:
                    continue

                seen.add(
                    value.name
                )

                features.append(
                    value
                )

        return features

    def discover(
        self,
    ) -> list[DynamicFeature]:
        """
        Discover all dynamic features.
        """

        modules = (
            self.discover_modules()
        )

        return self.discover_features(
            modules
        )