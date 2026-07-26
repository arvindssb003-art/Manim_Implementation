from __future__ import annotations

from typing import Any

from .integration import DynamicIntegration


class DynamicCodeBridge:
    """
    Bridge dynamically discovered features into the
    existing AnimForge code-generation pipeline.

    The existing static parser and generator remain untouched.

    Dynamic commands are detected from the original prompt
    and generated separately.

    Example:

        SCENE: Dynamic Demo

        CIRCLE a: red at center
        ARC arc1: green radius=2 start=0 angle=180 below a
        GRAPH parabola: blue y=x^2 below arc1

    Static commands continue through the existing pipeline.

    Dynamic commands are handled by DynamicIntegration.
    """

    def __init__(
        self,
        integration: DynamicIntegration | None = None,
    ) -> None:
        self.integration = (
            integration
            or DynamicIntegration()
        )

    def can_generate(
        self,
        line: str,
    ) -> bool:
        """
        Return True if the dynamic system can handle
        the given command line.
        """

        return self.integration.can_handle(
            line
        )

    def parse(
        self,
        line: str,
    ) -> Any | None:
        """
        Parse a dynamic object line.

        Returns None when the line is not dynamic.
        """

        return self.integration.try_parse(
            line
        )

    def generate(
        self,
        line: str,
    ) -> list[str] | None:
        """
        Generate Manim code for a dynamic object line.

        Returns None when the line is not dynamic.
        """

        return self.integration.try_generate(
            line
        )

    def dynamic_lines(
        self,
        prompt: str,
    ) -> list[str]:
        """
        Extract dynamic command lines from a complete prompt.

        The first line is assumed to be the SCENE declaration.

        Non-dynamic lines are ignored.

        Existing static parsing is completely untouched.
        """

        lines = [
            line.strip()
            for line in prompt.splitlines()
            if line.strip()
        ]

        dynamic: list[str] = []

        for line in lines:

            if self.can_generate(
                line
            ):
                dynamic.append(
                    line
                )

        return dynamic

    def generate_prompt(
        self,
        prompt: str,
    ) -> list[str]:
        """
        Generate Manim code for all dynamic commands
        contained in a complete prompt.

        Non-dynamic commands are ignored.

        This method is the main integration point for
        the higher-level pipeline.
        """

        return self.generate_objects(
            self.dynamic_lines(
                prompt
            )
        )

    def generate_objects(
        self,
        lines: list[str],
    ) -> list[str]:
        """
        Generate code for all dynamic object lines.

        Non-dynamic lines are ignored.

        The existing static parser remains responsible
        for static objects.
        """

        generated: list[str] = []

        for line in lines:

            if not self.can_generate(
                line
            ):
                continue

            code = self.generate(
                line
            )

            if code is None:
                continue

            generated.extend(
                code
            )

            generated.append(
                ""
            )

        return generated