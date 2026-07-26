from __future__ import annotations

from typing import Any

from .dispatcher import DynamicCommandDispatcher


class DynamicIntegration:
    """
    Safe integration boundary between the existing AnimForge
    system and the dynamic feature system.

    Existing static parsing and code generation remain untouched.

    The integration layer only answers:

        1. Can the dynamic system handle this command?
        2. If yes, parse it dynamically.
        3. If yes, generate dynamic code.

    The caller can then decide whether to fall back to the
    existing static implementation.
    """

    def __init__(
        self,
        dispatcher: DynamicCommandDispatcher | None = None,
    ) -> None:
        """
        Initialize the dynamic integration boundary.
        """

        self.dispatcher = (
            dispatcher
            or DynamicCommandDispatcher()
        )

    def can_handle(
        self,
        command: str,
    ) -> bool:
        """
        Return True when a dynamic feature supports
        the given command.
        """

        command_name = (
            command.strip()
            .split(
                None,
                1,
            )[0]
            .lower()
        )

        if not command_name:
            return False

        return self.dispatcher.has(
            command_name
        )

    def parse(
        self,
        line: str,
    ) -> Any:
        """
        Parse a dynamic command line.

        Raises:
            ValueError:
                If the command is not dynamically supported.
        """

        return self.dispatcher.dispatch_line(
            line
        )

    def generate(
        self,
        line: str,
    ) -> list[str]:
        """
        Generate Manim code for a dynamic command line.

        Raises:
            ValueError:
                If the command is not dynamically supported.
        """

        return self.dispatcher.generate_line(
            line
        )

    def try_parse(
        self,
        line: str,
    ) -> Any | None:
        """
        Try to parse a dynamic command.

        Returns:
            Parsed object if dynamically supported.
            None otherwise.

        This method is useful as a safe fallback boundary
        before calling the existing static parser.
        """

        if not self.can_handle(
            line
        ):
            return None

        return self.parse(
            line
        )

    def try_generate(
        self,
        line: str,
    ) -> list[str] | None:
        """
        Try to generate dynamic code.

        Returns:
            Generated code if dynamically supported.
            None otherwise.

        Existing static generation can be used when this
        returns None.
        """

        if not self.can_handle(
            line
        ):
            return None

        return self.generate(
            line
        )