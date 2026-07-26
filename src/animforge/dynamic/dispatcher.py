from __future__ import annotations

import re
from typing import Any

from .adapter import DynamicFeatureAdapter
from .discovery import DynamicFeatureDiscovery


class DynamicCommandDispatcher:
    """
    Dispatch dynamic AnimForge commands.

    The dispatcher provides a small, stable integration layer
    between the command-line syntax and dynamically discovered
    features.

    Example:

        ARC arc1: red radius=2 start=0 angle=180 at center

        GRAPH parabola: blue y=x^2 at center

    Dynamic feature modules are discovered automatically.
    """

    def __init__(
        self,
        adapter: DynamicFeatureAdapter | None = None,
        discovery: DynamicFeatureDiscovery | None = None,
    ) -> None:
        """
        Initialize the dynamic command dispatcher.

        Args:
            adapter:
                Optional dynamic feature adapter.

            discovery:
                Optional dynamic feature discovery service.
        """

        self.adapter = (
            adapter
            or DynamicFeatureAdapter()
        )

        self.discovery = (
            discovery
            or DynamicFeatureDiscovery()
        )

        self.discover()

    def discover(
        self,
    ) -> list[str]:
        """
        Discover and register dynamic features.

        Returns:
            Names of newly registered features.
        """

        features = (
            self.discovery.discover()
        )

        registered: list[str] = []

        for feature in features:

            if self.adapter.has(
                feature.name
            ):
                continue

            self.adapter.register(
                feature
            )

            registered.append(
                feature.name
            )

        return registered

    def dispatch(
        self,
        command: str,
        value: str,
    ) -> Any:
        """
        Dispatch a command to its dynamic feature.

        This method preserves the historical adapter API:

            dispatch(
                "arc",
                "arc1: red radius=2 ..."
            )

        Dynamic feature parsers, however, receive the complete
        command line so they can parse their own syntax.

        This allows feature-specific grammars such as:

            GRAPH parabola: blue y=x^2 at center

        without requiring the core dispatcher to understand
        feature-specific syntax.
        """

        command = (
            command
            .strip()
            .lower()
        )

        if not command:
            raise ValueError(
                "Dynamic command cannot be empty."
            )

        if not self.adapter.has(
            command
        ):
            raise ValueError(
                f"Unknown dynamic command: "
                f"'{command}'. "
                f"Available commands: "
                f"{self.adapter.list_features()}"
            )

        full_line = (
            f"{command} {value.strip()}"
        )

        return self.adapter.parse(
            command,
            full_line,
        )

    def dispatch_line(
        self,
        line: str,
    ) -> Any:
        """
        Parse a complete dynamic command line
        and dispatch it.

        Example:

            ARC arc1: red radius=2 at center

        The command name is extracted only for routing.
        The complete original line is passed to the
        dynamic feature parser.
        """

        line = line.strip()

        match = re.match(
            r"^([A-Za-z_][A-Za-z0-9_]*)\s+(.+)$",
            line,
        )

        if not match:
            raise ValueError(
                "Invalid dynamic command syntax."
            )

        command = (
            match.group(1)
        )

        if not self.adapter.has(
            command.lower()
        ):
            raise ValueError(
                f"Unknown dynamic command: "
                f"'{command}'. "
                f"Available commands: "
                f"{self.adapter.list_features()}"
            )

        return self.adapter.parse(
            command.lower(),
            line,
        )

    def generate(
        self,
        command: str,
        parsed: Any,
    ) -> Any:
        """
        Generate output for a parsed dynamic feature.
        """

        command = (
            command
            .strip()
            .lower()
        )

        if not self.adapter.has(
            command
        ):
            raise ValueError(
                f"Unknown dynamic command: "
                f"'{command}'. "
                f"Available commands: "
                f"{self.adapter.list_features()}"
            )

        return self.adapter.generate(
            command,
            parsed,
        )

    def generate_line(
        self,
        line: str,
    ) -> Any:
        """
        Parse a complete dynamic command line
        and generate its output.

        Example:

            GRAPH parabola: blue y=x^2 at center
        """

        line = line.strip()

        match = re.match(
            r"^([A-Za-z_][A-Za-z0-9_]*)\s+(.+)$",
            line,
        )

        if not match:
            raise ValueError(
                "Invalid dynamic command syntax."
            )

        command = (
            match.group(1)
            .lower()
        )

        parsed = self.dispatch_line(
            line
        )

        return self.generate(
            command,
            parsed,
        )

    def has(
        self,
        command: str,
    ) -> bool:
        """
        Return whether a dynamic feature exists.
        """

        return self.adapter.has(
            command.strip().lower()
        )

    def list_features(
        self,
    ) -> list[str]:
        """
        Return all currently registered
        dynamic feature names.
        """

        return self.adapter.list_features()