from __future__ import annotations

from animforge.models import (
    Animation,
    ArrowObject,
    LineObject,
    Scene,
)

from animforge.parser.errors import ParserError


class ValidationError(ValueError):
    """Raised when an animation scene is invalid."""


class SceneValidator:
    """
    Validate a parsed AnimForge scene.

    Validation is performed before Manim code generation.
    """

    def validate(self, scene: Scene) -> None:
        """
        Validate a complete scene.

        Args:
            scene: Parsed AnimForge scene.

        Raises:
            ValidationError: If the scene is invalid.
        """

        self._validate_duplicate_ids(scene)
        self._validate_relative_positions(scene)
        self._validate_connections(scene)
        self._validate_animation_targets(scene)
        self._validate_circular_dependencies(scene)

    def _validate_duplicate_ids(
        self,
        scene: Scene,
    ) -> None:
        """Ensure every object has a unique ID."""

        object_ids: set[str] = set()

        for obj in scene.objects:
            if obj.id in object_ids:
                raise ValidationError(
                    f"Duplicate object ID: '{obj.id}'."
                )

            object_ids.add(obj.id)

    def _validate_relative_positions(
        self,
        scene: Scene,
    ) -> None:
        """Validate relative-position references."""

        object_ids = self._get_object_ids(scene)

        for obj in scene.objects:
            if obj.relative_position is None:
                continue

            target = obj.relative_position.target

            if target not in object_ids:
                raise ValidationError(
                    f"Object '{obj.id}' has a relative "
                    f"position referencing unknown object "
                    f"'{target}'."
                )

            if target == obj.id:
                raise ValidationError(
                    f"Object '{obj.id}' cannot be positioned "
                    "relative to itself."
                )

    def _validate_connections(
        self,
        scene: Scene,
    ) -> None:
        """Validate line and arrow object references."""

        object_ids = self._get_object_ids(scene)

        for obj in scene.objects:

            if isinstance(obj, ArrowObject):
                self._validate_reference(
                    source_id=obj.id,
                    reference=obj.start,
                    object_ids=object_ids,
                    reference_name="arrow start",
                )

                self._validate_reference(
                    source_id=obj.id,
                    reference=obj.end,
                    object_ids=object_ids,
                    reference_name="arrow end",
                )

            elif isinstance(obj, LineObject):
                self._validate_reference(
                    source_id=obj.id,
                    reference=obj.start,
                    object_ids=object_ids,
                    reference_name="line start",
                )

                self._validate_reference(
                    source_id=obj.id,
                    reference=obj.end,
                    object_ids=object_ids,
                    reference_name="line end",
                )

    @staticmethod
    def _validate_reference(
        source_id: str,
        reference: str,
        object_ids: set[str],
        reference_name: str,
    ) -> None:
        """Validate a single object reference."""

        if reference not in object_ids:
            raise ValidationError(
                f"Object '{source_id}' has an invalid "
                f"{reference_name} reference: "
                f"'{reference}'."
            )

    def _validate_animation_targets(
        self,
        scene: Scene,
    ) -> None:
        """Ensure every animation targets an existing object."""

        object_ids = self._get_object_ids(scene)

        for animation in scene.animations:
            if animation.target not in object_ids:
                raise ValidationError(
                    f"Animation targets unknown object "
                    f"'{animation.target}'."
                )

    def _validate_circular_dependencies(
        self,
        scene: Scene,
    ) -> None:
        """
        Detect circular relative-position dependencies.

        Example of an invalid layout:

            A below B
            B below C
            C below A
        """

        graph: dict[str, str] = {}

        for obj in scene.objects:
            if obj.relative_position is not None:
                graph[obj.id] = (
                    obj.relative_position.target
                )

        for object_id in graph:
            visited: set[str] = set()
            current = object_id

            while current in graph:
                if current in visited:
                    raise ValidationError(
                        "Circular relative-position "
                        f"dependency detected involving "
                        f"object '{current}'."
                    )

                visited.add(current)
                current = graph[current]

    @staticmethod
    def _get_object_ids(
        scene: Scene,
    ) -> set[str]:
        """Return all object IDs in a scene."""

        return {
            obj.id
            for obj in scene.objects
        }