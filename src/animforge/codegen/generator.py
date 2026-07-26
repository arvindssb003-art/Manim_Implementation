from __future__ import annotations

import ast
import keyword
import re

from animforge.codegen.objects import (
    ObjectGeneratorRegistry,
)
from animforge.models import (
    Animation,
    AnimationType,
    Position,
    Scene,
)

from animforge.validation import SceneValidator


class CodeGenerationError(ValueError):
    """Raised when Manim code generation fails."""


class ManimCodeGenerator:
    """
    Generate deterministic Manim Python code from a validated Scene.

    Object-specific code generation is delegated to the
    ObjectGeneratorRegistry.

    The optional target_duration parameter ensures that the
    generated Manim scene lasts at least the requested duration.
    """

    def __init__(
        self,
        object_registry: ObjectGeneratorRegistry | None = None,
    ) -> None:
        self.object_registry = (
            object_registry
            or ObjectGeneratorRegistry()
        )

    def generate(
        self,
        scene: Scene,
        target_duration: float | None = None,
    ) -> str:
        """
        Generate complete Manim Python source code.

        Args:
            scene:
                AnimForge scene model.

            target_duration:
                Optional minimum target duration in seconds.

                If the generated animations finish before this
                duration, a final self.wait() is added to keep
                the video visible until the requested duration.

        Returns:
            Generated Manim Python source code.
        """

        if target_duration is not None:
            if target_duration <= 0:
                raise CodeGenerationError(
                    "Target duration must be greater than zero."
                )

        try:
            SceneValidator().validate(scene)

        except Exception as exc:
            raise CodeGenerationError(
                "Cannot generate code from "
                f"invalid scene: {exc}"
            ) from exc

        try:
            lines: list[str] = []

            lines.extend(
                self._generate_header()
            )

            lines.extend(
                self._generate_class(
                    scene,
                    target_duration=target_duration,
                )
            )

            source = "\n".join(lines)

            self.validate_python_syntax(source)

            return source

        except CodeGenerationError:
            raise

        except Exception as exc:
            raise CodeGenerationError(
                "Failed to generate "
                f"Manim code: {exc}"
            ) from exc

    @staticmethod
    def _generate_header() -> list[str]:
        return [
            "from manim import *",
            "",
            "",
        ]

    def _generate_class(
        self,
        scene: Scene,
        target_duration: float | None = None,
    ) -> list[str]:
        """
        Generate the Manim Scene class.

        The requested target duration is enforced by adding
        a final self.wait() when the generated animation
        timeline is shorter than the requested duration.
        """

        class_name = (
            self._class_name(
                scene.name
            )
        )

        lines = [
            f"class {class_name}(Scene):",
            "",
            "    def construct(self):",
            "",
        ]

        if not scene.objects:
            lines.append(
                "        pass"
            )

            return lines

        variable_map = (
            self._build_variable_map(
                scene
            )
        )

        # Generate objects.
        for obj in scene.objects:

            object_lines = (
                self._generate_object(
                    obj,
                    variable_map,
                )
            )

            lines.extend(
                f"        {line}"
                for line in object_lines
            )

            lines.append("")

        # Generate animations.
        total_animation_duration = 0.0

        for animation in scene.animations:

            animation_lines = (
                self._generate_animation(
                    animation
                )
            )

            lines.extend(
                f"        {line}"
                for line in animation_lines
            )

            lines.append("")

            try:
                total_animation_duration += float(
                    animation.duration
                )

            except (
                TypeError,
                ValueError,
            ):
                raise CodeGenerationError(
                    "Invalid animation duration: "
                    f"{animation.duration}"
                )

        # Ensure requested target duration.
        if target_duration is not None:

            remaining_duration = (
                float(target_duration)
                - total_animation_duration
            )

            if remaining_duration > 0:

                lines.append(
                    "        # Keep the final "
                    "scene visible until the "
                    "requested duration."
                )

                lines.append(
                    f"        self.wait("
                    f"{remaining_duration:.3f}"
                    f")"
                )

                lines.append("")

        return lines

    def _build_variable_map(
        self,
        scene: Scene,
    ) -> dict[str, str]:

        variable_map: dict[
            str,
            str,
        ] = {}

        for obj in scene.objects:

            variable_map[
                obj.id
            ] = self._variable_name(
                obj.id
            )

        return variable_map

    def _generate_object(
        self,
        obj,
        variable_map: dict[str, str],
    ) -> list[str]:

        variable = (
            variable_map[
                obj.id
            ]
        )

        object_type = (
            self._object_type(
                obj
            )
        )

        object_type = (
            self._normalize_object_type(
                object_type
            )
        )

        try:
            generator = (
                self.object_registry.get(
                    object_type
                )
            )

        except ValueError as exc:
            raise CodeGenerationError(
                "Unsupported object type: "
                f"'{object_type}' "
                f"for object '{obj.id}'."
            ) from exc

        try:
            return generator.generate(
                obj=obj,
                variable_name=variable,
                variable_map=variable_map,
            )

        except CodeGenerationError:
            raise

        except Exception as exc:
            raise CodeGenerationError(
                "Failed to generate code "
                f"for object '{obj.id}': "
                f"{exc}"
            ) from exc

    @staticmethod
    def _object_type(
        obj,
    ) -> str:

        class_name = (
            type(obj)
            .__name__
        )

        if class_name.endswith(
            "Object"
        ):
            class_name = (
                class_name[
                    :-len("Object")
                ]
            )

        return (
            class_name.lower()
        )

    @staticmethod
    def _normalize_object_type(
        object_type: str,
    ) -> str:

        normalized = (
            object_type
            .strip()
            .lower()
            .replace(
                "-",
                "_",
            )
            .replace(
                " ",
                "_",
            )
        )

        aliases = {
            "roundedrectangle": (
                "rounded_rectangle"
            ),
            "rounded_rect": (
                "rounded_rectangle"
            ),
            "dashedline": (
                "dashed_line"
            ),
        }

        return aliases.get(
            normalized,
            normalized,
        )

    def _generate_animation(
        self,
        animation: Animation,
    ) -> list[str]:

        target = (
            self._variable_name(
                animation.target
            )
        )

        duration = (
            animation.duration
        )

        animation_map = {
            AnimationType.WRITE: (
                f"self.play("
                f"Write({target}), "
                f"run_time={duration}"
                f")"
            ),

            AnimationType.FADE_IN: (
                f"self.play("
                f"FadeIn({target}), "
                f"run_time={duration}"
                f")"
            ),

            AnimationType.FADE_OUT: (
                f"self.play("
                f"FadeOut({target}), "
                f"run_time={duration}"
                f")"
            ),

            AnimationType.GROW: (
                f"self.play("
                f"GrowFromCenter({target}), "
                f"run_time={duration}"
                f")"
            ),
        }

        if (
            animation.animation_type
            not in animation_map
        ):
            raise CodeGenerationError(
                "Animation type "
                f"'{animation.animation_type.value}' "
                "is not supported by "
                "the generator yet."
            )

        return [
            animation_map[
                animation.animation_type
            ]
        ]

    @staticmethod
    def _generate_position(
        variable: str,
        obj,
    ) -> list[str]:

        lines: list[str] = []

        if obj.position:

            position_map = {
                Position.CENTER:
                    f"{variable}.move_to(ORIGIN)",

                Position.TOP:
                    f"{variable}.to_edge(UP)",

                Position.BOTTOM:
                    f"{variable}.to_edge(DOWN)",

                Position.LEFT:
                    f"{variable}.to_edge(LEFT)",

                Position.RIGHT:
                    f"{variable}.to_edge(RIGHT)",

                Position.TOP_LEFT:
                    f"{variable}.to_corner(UL)",

                Position.TOP_RIGHT:
                    f"{variable}.to_corner(UR)",

                Position.BOTTOM_LEFT:
                    f"{variable}.to_corner(DL)",

                Position.BOTTOM_RIGHT:
                    f"{variable}.to_corner(DR)",
            }

            try:
                lines.append(
                    position_map[
                        obj.position
                    ]
                )

            except KeyError as exc:
                raise CodeGenerationError(
                    "Unsupported position: "
                    f"{obj.position}"
                ) from exc

        elif obj.relative_position:

            target = (
                ManimCodeGenerator
                ._variable_name(
                    obj.relative_position.target
                )
            )

            relation = (
                obj.relative_position
                .relation
                .value
            )

            direction_map = {
                "below": "DOWN",
                "above": "UP",
                "left_of": "LEFT",
                "right_of": "RIGHT",
            }

            if relation not in direction_map:
                raise CodeGenerationError(
                    "Unsupported relative "
                    f"position: {relation}"
                )

            direction = (
                direction_map[
                    relation
                ]
            )

            lines.append(
                f"{variable}.next_to("
                f"{target}, "
                f"{direction}"
                f")"
            )

        return lines

    @staticmethod
    def _color_constant(
        color: str,
    ) -> str:

        color_map = {
            "red": "RED",
            "blue": "BLUE",
            "green": "GREEN",
            "yellow": "YELLOW",
            "orange": "ORANGE",
            "purple": "PURPLE",
            "pink": "PINK",
            "white": "WHITE",
            "black": "BLACK",
        }

        normalized = (
            color.lower()
        )

        return color_map.get(
            normalized,
            "WHITE",
        )

    @staticmethod
    def _variable_name(
        object_id: str,
    ) -> str:

        name = re.sub(
            r"\W+",
            "_",
            object_id,
        )

        name = name.strip(
            "_"
        )

        if not name:
            raise CodeGenerationError(
                "Object ID cannot be converted "
                "to a Python variable name."
            )

        if name[0].isdigit():
            name = (
                f"object_{name}"
            )

        if keyword.iskeyword(
            name
        ):
            name = (
                f"{name}_obj"
            )

        return (
            f"{name}_obj"
        )

    @staticmethod
    def _class_name(
        scene_name: str,
    ) -> str:

        words = re.findall(
            r"[A-Za-z0-9]+",
            scene_name,
        )

        if not words:
            return "GeneratedScene"

        class_name = "".join(
            word.capitalize()
            for word in words
        )

        if class_name[0].isdigit():
            class_name = (
                f"Generated{class_name}"
            )

        return (
            f"{class_name}Scene"
        )

    @staticmethod
    def validate_python_syntax(
        source: str,
    ) -> None:

        try:
            ast.parse(
                source
            )

        except SyntaxError as exc:
            raise CodeGenerationError(
                "Generated Manim code "
                "contains invalid Python "
                f"syntax: {exc}"
            ) from exc