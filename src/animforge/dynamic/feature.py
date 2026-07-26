from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class DynamicFeature:
    """Definition of a dynamically registered AnimForge feature."""

    name: str

    parser: Callable[..., Any]

    generator: Callable[..., Any]

    model: type[Any] | None = None