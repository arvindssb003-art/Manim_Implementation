from enum import Enum

from pydantic import BaseModel, Field


class AnimationType(str, Enum):
    """Supported animation types."""

    WRITE = "write"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    GROW = "grow"
    MOVE = "move"
    SHIFT = "shift"
    ROTATE = "rotate"
    SCALE = "scale"


class Animation(BaseModel):
    """Represents an animation applied to a scene object."""

    target: str = Field(min_length=1)
    animation_type: AnimationType
    duration: float = Field(default=1.0, gt=0)