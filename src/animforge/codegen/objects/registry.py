from __future__ import annotations

import importlib
import inspect
import pkgutil

from animforge.codegen.objects.arrow import (
    ArrowObjectCodeGenerator,
)
from animforge.codegen.objects.base import (
    ObjectCodeGenerator,
)
from animforge.codegen.objects.circle import (
    CircleObjectCodeGenerator,
)
from animforge.codegen.objects.dot import (
    DotObjectCodeGenerator,
)
from animforge.codegen.objects.ellipse import (
    EllipseObjectCodeGenerator,
)
from animforge.codegen.objects.line import (
    LineObjectCodeGenerator,
)
from animforge.codegen.objects.polygon import (
    PolygonObjectCodeGenerator,
)
from animforge.codegen.objects.rectangle import (
    RectangleObjectCodeGenerator,
)
from animforge.codegen.objects.rounded_rectangle import (
    RoundedRectangleObjectCodeGenerator,
)
from animforge.codegen.objects.square import (
    SquareObjectCodeGenerator,
)
from animforge.codegen.objects.text import (
    TextObjectCodeGenerator,
)
from animforge.codegen.objects.triangle import (
    TriangleObjectCodeGenerator,
)


class ObjectGeneratorRegistry:
    """
    Hybrid registry for object-specific Manim code generators.

    Core generators are registered explicitly and remain stable.

    Additional generators can be discovered dynamically from
    animforge.codegen.objects.

    Explicitly registered generators always take precedence
    over dynamically discovered generators.
    """

    def __init__(
        self,
        generators: list[
            ObjectCodeGenerator
        ] | None = None,
        auto_discover: bool = True,
    ) -> None:

        if generators is None:
            generators = [
                TextObjectCodeGenerator(),
                CircleObjectCodeGenerator(),
                RectangleObjectCodeGenerator(),
                LineObjectCodeGenerator(),
                ArrowObjectCodeGenerator(),
                DotObjectCodeGenerator(),
                SquareObjectCodeGenerator(),
                TriangleObjectCodeGenerator(),
                EllipseObjectCodeGenerator(),
                RoundedRectangleObjectCodeGenerator(),
                PolygonObjectCodeGenerator(),
            ]

        self._generators: dict[
            str,
            ObjectCodeGenerator,
        ] = {}

        # Register stable core generators first.
        for generator in generators:
            self.register(generator)

        # Discover additional generators without
        # replacing explicitly registered generators.
        if auto_discover:
            self._discover_generators()

    def register(
        self,
        generator: ObjectCodeGenerator,
        overwrite: bool = True,
    ) -> None:
        """
        Register an object generator.

        Args:
            generator:
                Generator instance to register.

            overwrite:
                Whether an existing generator with the same
                object type may be replaced.
        """

        object_type = (
            generator.object_type
            .strip()
            .lower()
        )

        if (
            object_type in self._generators
            and not overwrite
        ):
            return

        self._generators[
            object_type
        ] = generator

    def _discover_generators(
        self,
    ) -> None:
        """
        Dynamically discover ObjectCodeGenerator subclasses.

        Discovery is intentionally best-effort.

        If a module cannot be imported or a generator cannot
        be instantiated, it is skipped rather than breaking
        the stable core registry.
        """

        import animforge.codegen.objects as objects_package

        for module_info in pkgutil.iter_modules(
            objects_package.__path__
        ):
            module_name = (
                module_info.name
            )

            # Skip infrastructure modules.
            if module_name in {
                "base",
                "registry",
                "__init__",
            }:
                continue

            try:
                module = importlib.import_module(
                    f"{objects_package.__name__}.{module_name}"
                )

            except Exception:
                continue

            for _, candidate in inspect.getmembers(
                module,
                inspect.isclass,
            ):
                if candidate is ObjectCodeGenerator:
                    continue

                if not issubclass(
                    candidate,
                    ObjectCodeGenerator,
                ):
                    continue

                if inspect.isabstract(
                    candidate
                ):
                    continue

                try:
                    generator = candidate()

                except Exception:
                    continue

                object_type = (
                    generator.object_type
                    .strip()
                    .lower()
                )

                # Core/static generators always win.
                if object_type not in self._generators:
                    self._generators[
                        object_type
                    ] = generator

    def get(
        self,
        object_type: str,
    ) -> ObjectCodeGenerator:
        """Get a generator for an object type."""

        normalized_type = (
            object_type
            .strip()
            .lower()
        )

        generator = (
            self._generators.get(
                normalized_type
            )
        )

        if generator is None:
            raise ValueError(
                "Unsupported object type: "
                f"'{object_type}'. "
                "Supported object types: "
                f"{self.supported_types()}."
            )

        return generator

    def supports(
        self,
        object_type: str,
    ) -> bool:
        """Check whether an object type is supported."""

        normalized_type = (
            object_type
            .strip()
            .lower()
        )

        return (
            normalized_type
            in self._generators
        )

    def supported_types(
        self,
    ) -> list[str]:
        """Return all supported object types."""

        return sorted(
            self._generators.keys()
        )