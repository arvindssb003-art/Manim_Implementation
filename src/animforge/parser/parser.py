from __future__ import annotations

import re

from animforge.models import (
    Animation,
    AnimationType,
    ArrowObject,
    CircleObject,
    DotObject,
    EllipseObject,
    LineObject,
    PolygonObject,
    Position,
    RectangleObject,
    RelativePosition,
    RelationType,
    RoundedRectangleObject,
    Scene,
    SquareObject,
    TextObject,
    TriangleObject,
)

from .errors import ParserError


class PromptParser:
    """
    Parse the AnimForge structured animation prompt language.

    Example:

        SCENE: Basic Shapes

        TEXT title: "Basic Shapes" at top
        DOT point: red below title
        CIRCLE circle: blue below point
        SQUARE square: blue below circle
        TRIANGLE triangle: green below square
        ELLIPSE ellipse: yellow below triangle
        ROUNDED_RECTANGLE box: purple below ellipse
        POLYGON polygon: orange below box

        ANIMATE title: write
        ANIMATE point: grow
        ANIMATE polygon: grow
    """

    def parse(self, prompt: str) -> Scene:
        """Parse a complete animation prompt."""

        if not prompt or not prompt.strip():
            raise ParserError(
                "Prompt cannot be empty."
            )

        lines = self._clean_lines(prompt)

        if not lines:
            raise ParserError(
                "Prompt does not contain any commands."
            )

        scene_name = self._parse_scene_line(
            lines[0]
        )

        scene = Scene(
            name=scene_name
        )

        for line_number, line in enumerate(
            lines[1:],
            start=2,
        ):
            try:

                if line.upper().startswith(
                    "TEXT "
                ):
                    scene.add_object(
                        self._parse_text(line)
                    )

                elif line.upper().startswith(
                    "CIRCLE "
                ):
                    scene.add_object(
                        self._parse_circle(line)
                    )

                elif line.upper().startswith(
                    "RECTANGLE "
                ):
                    scene.add_object(
                        self._parse_rectangle(line)
                    )

                elif line.upper().startswith(
                    "ROUNDED_RECTANGLE "
                ):
                    scene.add_object(
                        self._parse_rounded_rectangle(
                            line
                        )
                    )

                elif line.upper().startswith(
                    "SQUARE "
                ):
                    scene.add_object(
                        self._parse_square(line)
                    )

                elif line.upper().startswith(
                    "TRIANGLE "
                ):
                    scene.add_object(
                        self._parse_triangle(line)
                    )

                elif line.upper().startswith(
                    "ELLIPSE "
                ):
                    scene.add_object(
                        self._parse_ellipse(line)
                    )

                elif line.upper().startswith(
                    "DOT "
                ):
                    scene.add_object(
                        self._parse_dot(line)
                    )

                elif line.upper().startswith(
                    "POLYGON "
                ):
                    scene.add_object(
                        self._parse_polygon(line)
                    )

                elif line.upper().startswith(
                    "LINE "
                ):
                    scene.add_object(
                        self._parse_line(line)
                    )

                elif line.upper().startswith(
                    "ARROW "
                ):
                    scene.add_object(
                        self._parse_arrow(line)
                    )

                elif line.upper().startswith(
                    "ANIMATE "
                ):
                    scene.add_animation(
                        self._parse_animation(line)
                    )

                else:
                    raise ParserError(
                        f"Unsupported command: '{line}'"
                    )

            except ParserError as exc:
                raise ParserError(
                    f"Line {line_number}: {exc}"
                ) from exc

        return scene

    @staticmethod
    def _clean_lines(
        prompt: str,
    ) -> list[str]:
        """Remove blank lines and whitespace."""

        return [
            line.strip()
            for line in prompt.splitlines()
            if line.strip()
        ]

    @staticmethod
    def _parse_scene_line(
        line: str,
    ) -> str:
        """Parse the SCENE declaration."""

        match = re.fullmatch(
            r"SCENE:\s*(.+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "First command must be "
                "'SCENE: <scene name>'."
            )

        return match.group(1).strip()

    @staticmethod
    def _parse_text(
        line: str,
    ) -> TextObject:
        """Parse a TEXT command."""

        match = re.fullmatch(
            r'TEXT\s+(\w+):\s*"(.+)"\s+'
            r"(at|below|above|left_of|right_of)\s+(\w+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "Invalid TEXT syntax."
            )

        object_id, content, relation, target = (
            match.groups()
        )

        if relation.lower() == "at":
            position = (
                PromptParser._parse_position(
                    target
                )
            )

            return TextObject(
                id=object_id,
                content=content,
                position=position,
            )

        relative_position = (
            PromptParser._parse_relative_position(
                relation,
                target,
            )
        )

        return TextObject(
            id=object_id,
            content=content,
            relative_position=relative_position,
        )

    @staticmethod
    def _parse_circle(
        line: str,
    ) -> CircleObject:
        """Parse a CIRCLE command."""

        match = re.fullmatch(
            r"CIRCLE\s+(\w+):\s*(\w+)\s+"
            r"(at|below|above|left_of|right_of)\s+"
            r"(\w+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "Invalid CIRCLE syntax."
            )

        object_id, color, relation, target = (
            match.groups()
        )

        if relation.lower() == "at":
            position = (
                PromptParser._parse_position(
                    target
                )
            )

            return CircleObject(
                id=object_id,
                color=color.lower(),
                position=position,
            )

        relative_position = (
            PromptParser._parse_relative_position(
                relation,
                target,
            )
        )

        return CircleObject(
            id=object_id,
            color=color.lower(),
            relative_position=relative_position,
        )

    @staticmethod
    def _parse_rectangle(
        line: str,
    ) -> RectangleObject:
        """Parse a RECTANGLE command."""

        match = re.fullmatch(
            r"RECTANGLE\s+(\w+):\s*(\w+)\s+"
            r"(at|below|above|left_of|right_of)\s+"
            r"(\w+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "Invalid RECTANGLE syntax."
            )

        object_id, color, relation, target = (
            match.groups()
        )

        if relation.lower() == "at":
            position = (
                PromptParser._parse_position(
                    target
                )
            )

            return RectangleObject(
                id=object_id,
                color=color.lower(),
                position=position,
            )

        relative_position = (
            PromptParser._parse_relative_position(
                relation,
                target,
            )
        )

        return RectangleObject(
            id=object_id,
            color=color.lower(),
            relative_position=relative_position,
        )

    @staticmethod
    def _parse_rounded_rectangle(
        line: str,
    ) -> RoundedRectangleObject:
        """Parse a ROUNDED_RECTANGLE command."""

        match = re.fullmatch(
            r"ROUNDED_RECTANGLE\s+(\w+):\s*(\w+)\s+"
            r"(at|below|above|left_of|right_of)\s+"
            r"(\w+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "Invalid ROUNDED_RECTANGLE syntax."
            )

        object_id, color, relation, target = (
            match.groups()
        )

        if relation.lower() == "at":
            return RoundedRectangleObject(
                id=object_id,
                color=color.lower(),
                position=(
                    PromptParser._parse_position(
                        target
                    )
                ),
            )

        return RoundedRectangleObject(
            id=object_id,
            color=color.lower(),
            relative_position=(
                PromptParser._parse_relative_position(
                    relation,
                    target,
                )
            ),
        )

    @staticmethod
    def _parse_square(
        line: str,
    ) -> SquareObject:
        """Parse a SQUARE command."""

        match = re.fullmatch(
            r"SQUARE\s+(\w+):\s*(\w+)\s+"
            r"(at|below|above|left_of|right_of)\s+"
            r"(\w+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "Invalid SQUARE syntax."
            )

        object_id, color, relation, target = (
            match.groups()
        )

        if relation.lower() == "at":
            return SquareObject(
                id=object_id,
                color=color.lower(),
                position=(
                    PromptParser._parse_position(
                        target
                    )
                ),
            )

        return SquareObject(
            id=object_id,
            color=color.lower(),
            relative_position=(
                PromptParser._parse_relative_position(
                    relation,
                    target,
                )
            ),
        )

    @staticmethod
    def _parse_triangle(
        line: str,
    ) -> TriangleObject:
        """Parse a TRIANGLE command."""

        match = re.fullmatch(
            r"TRIANGLE\s+(\w+):\s*(\w+)\s+"
            r"(at|below|above|left_of|right_of)\s+"
            r"(\w+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "Invalid TRIANGLE syntax."
            )

        object_id, color, relation, target = (
            match.groups()
        )

        if relation.lower() == "at":
            return TriangleObject(
                id=object_id,
                color=color.lower(),
                position=(
                    PromptParser._parse_position(
                        target
                    )
                ),
            )

        return TriangleObject(
            id=object_id,
            color=color.lower(),
            relative_position=(
                PromptParser._parse_relative_position(
                    relation,
                    target,
                )
            ),
        )

    @staticmethod
    def _parse_ellipse(
        line: str,
    ) -> EllipseObject:
        """Parse an ELLIPSE command."""

        match = re.fullmatch(
            r"ELLIPSE\s+(\w+):\s*(\w+)\s+"
            r"(at|below|above|left_of|right_of)\s+"
            r"(\w+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "Invalid ELLIPSE syntax."
            )

        object_id, color, relation, target = (
            match.groups()
        )

        if relation.lower() == "at":
            return EllipseObject(
                id=object_id,
                color=color.lower(),
                position=(
                    PromptParser._parse_position(
                        target
                    )
                ),
            )

        return EllipseObject(
            id=object_id,
            color=color.lower(),
            relative_position=(
                PromptParser._parse_relative_position(
                    relation,
                    target,
                )
            ),
        )

    @staticmethod
    def _parse_dot(
        line: str,
    ) -> DotObject:
        """Parse a DOT command."""

        match = re.fullmatch(
            r"DOT\s+(\w+):\s*(\w+)\s+"
            r"(at|below|above|left_of|right_of)\s+"
            r"(\w+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "Invalid DOT syntax."
            )

        object_id, color, relation, target = (
            match.groups()
        )

        if relation.lower() == "at":
            return DotObject(
                id=object_id,
                color=color.lower(),
                position=(
                    PromptParser._parse_position(
                        target
                    )
                ),
            )

        return DotObject(
            id=object_id,
            color=color.lower(),
            relative_position=(
                PromptParser._parse_relative_position(
                    relation,
                    target,
                )
            ),
        )

    @staticmethod
    def _parse_polygon(
        line: str,
    ) -> PolygonObject:
        """Parse a POLYGON command.

        Supported syntax:

            POLYGON hexagon: blue at center
            POLYGON hexagon: blue sides=6 at center
            POLYGON hexagon: blue radius=1.5 at center
            POLYGON hexagon: blue sides=6 radius=1.5 at center
            POLYGON pentagon: green sides=5 radius=1.0 below hexagon
        """

        match = re.fullmatch(
            r"POLYGON\s+(\w+):\s*(\w+)"
            r"(?:\s+sides=(\d+))?"
            r"(?:\s+radius=(\d+(?:\.\d+)?))?\s+"
            r"(at|below|above|left_of|right_of)\s+"
            r"(\w+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "Invalid POLYGON syntax. "
                "Expected: "
                "POLYGON <id>: <color> "
                "[sides=<n>] [radius=<r>] "
                "at|below|above|left_of|right_of "
                "<target>."
            )

        (
            object_id,
            color,
            sides_value,
            radius_value,
            relation,
            target,
        ) = match.groups()

        sides = (
            int(sides_value)
            if sides_value is not None
            else 6
        )

        radius = (
            float(radius_value)
            if radius_value is not None
            else 1.0
        )

        if sides < 3:
            raise ParserError(
                "POLYGON sides must be at least 3."
            )

        if radius <= 0:
            raise ParserError(
                "POLYGON radius must be greater than 0."
            )

        if relation.lower() == "at":
            return PolygonObject(
                id=object_id,
                color=color.lower(),
                sides=sides,
                radius=radius,
                position=(
                    PromptParser._parse_position(
                        target
                    )
                ),
            )

        return PolygonObject(
            id=object_id,
            color=color.lower(),
            sides=sides,
            radius=radius,
            relative_position=(
                PromptParser._parse_relative_position(
                    relation,
                    target,
                )
            ),
        )

    @staticmethod
    def _parse_line(
        line: str,
    ) -> LineObject:
        """Parse a LINE command."""

        match = re.fullmatch(
            r"LINE\s+(\w+):\s*(\w+)\s+to\s+(\w+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "Invalid LINE syntax."
            )

        object_id, start, end = match.groups()

        return LineObject(
            id=object_id,
            start=start,
            end=end,
        )

    @staticmethod
    def _parse_arrow(
        line: str,
    ) -> ArrowObject:
        """Parse an ARROW command."""

        match = re.fullmatch(
            r"ARROW\s+(\w+):\s*(\w+)\s+to\s+(\w+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "Invalid ARROW syntax."
            )

        object_id, start, end = match.groups()

        return ArrowObject(
            id=object_id,
            start=start,
            end=end,
        )

    @staticmethod
    def _parse_animation(
        line: str,
    ) -> Animation:
        """Parse an ANIMATE command."""

        match = re.fullmatch(
            r"ANIMATE\s+(\w+):\s*(\w+)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ParserError(
                "Invalid ANIMATE syntax."
            )

        target, animation = match.groups()

        try:
            animation_type = AnimationType(
                animation.lower()
            )

        except ValueError as exc:
            supported = ", ".join(
                item.value
                for item in AnimationType
            )

            raise ParserError(
                f"Unsupported animation "
                f"'{animation}'. "
                f"Supported animations: "
                f"{supported}"
            ) from exc

        return Animation(
            target=target,
            animation_type=animation_type,
        )

    @staticmethod
    def _parse_position(
        value: str,
    ) -> Position:
        """Parse an absolute position."""

        try:
            return Position(
                value.lower()
            )

        except ValueError as exc:
            supported = ", ".join(
                item.value
                for item in Position
            )

            raise ParserError(
                f"Unsupported position "
                f"'{value}'. "
                f"Supported positions: "
                f"{supported}"
            ) from exc

    @staticmethod
    def _parse_relative_position(
        relation: str,
        target: str,
    ) -> RelativePosition:
        """Create a relative position."""

        try:
            relation_type = RelationType(
                relation.lower()
            )

        except ValueError as exc:
            raise ParserError(
                f"Unsupported relation "
                f"'{relation}'."
            ) from exc

        return RelativePosition(
            relation=relation_type,
            target=target,
        )
