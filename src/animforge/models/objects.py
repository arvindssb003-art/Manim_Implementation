from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ObjectType(str, Enum):
    """Supported animation object types."""

    TEXT = "text"
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    ROUNDED_RECTANGLE = "rounded_rectangle"
    SQUARE = "square"
    TRIANGLE = "triangle"
    ELLIPSE = "ellipse"
    DOT = "dot"
    POLYGON = "polygon"
    LINE = "line"
    ARROW = "arrow"


class Position(str, Enum):
    """Supported absolute positions."""

    CENTER = "center"
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


class RelationType(str, Enum):
    """Supported relative positioning relationships."""

    BELOW = "below"
    ABOVE = "above"
    LEFT_OF = "left_of"
    RIGHT_OF = "right_of"


class RelativePosition(BaseModel):
    """Defines the position of an object relative to another object."""

    relation: RelationType
    target: str = Field(min_length=1)


class AnimationObject(BaseModel):
    """Base model for an object in an animation scene."""

    id: str = Field(min_length=1)

    object_type: ObjectType

    position: Position | None = None

    relative_position: RelativePosition | None = None

    color: str | None = None


class TextObject(AnimationObject):
    """Text displayed in the animation."""

    object_type: ObjectType = ObjectType.TEXT

    content: str = Field(min_length=1)


class CircleObject(AnimationObject):
    """Circle displayed in the animation."""

    object_type: ObjectType = ObjectType.CIRCLE

    radius: float = Field(
        default=1.0,
        gt=0,
    )


class RectangleObject(AnimationObject):
    """Rectangle displayed in the animation."""

    object_type: ObjectType = ObjectType.RECTANGLE

    width: float = Field(
        default=2.0,
        gt=0,
    )

    height: float = Field(
        default=1.0,
        gt=0,
    )


class RoundedRectangleObject(AnimationObject):
    """Rounded rectangle displayed in the animation."""

    object_type: ObjectType = (
        ObjectType.ROUNDED_RECTANGLE
    )

    width: float = Field(
        default=2.0,
        gt=0,
    )

    height: float = Field(
        default=1.0,
        gt=0,
    )

    corner_radius: float = Field(
        default=0.2,
        gt=0,
    )


class SquareObject(AnimationObject):
    """Square displayed in the animation."""

    object_type: ObjectType = ObjectType.SQUARE

    side_length: float = Field(
        default=2.0,
        gt=0,
    )


class TriangleObject(AnimationObject):
    """Triangle displayed in the animation."""

    object_type: ObjectType = ObjectType.TRIANGLE

    side_length: float = Field(
        default=2.0,
        gt=0,
    )


class EllipseObject(AnimationObject):
    """Ellipse displayed in the animation."""

    object_type: ObjectType = ObjectType.ELLIPSE

    width: float = Field(
        default=2.0,
        gt=0,
    )

    height: float = Field(
        default=1.0,
        gt=0,
    )


class DotObject(AnimationObject):
    """Dot displayed in the animation."""

    object_type: ObjectType = ObjectType.DOT

    radius: float = Field(
        default=0.08,
        gt=0,
    )


class PolygonObject(AnimationObject):
    """Regular polygon displayed in the animation."""

    object_type: ObjectType = ObjectType.POLYGON

    sides: int = Field(
        default=6,
        ge=3,
    )

    radius: float = Field(
        default=1.0,
        gt=0,
    )


class LineObject(AnimationObject):
    """Line connecting two points."""

    object_type: ObjectType = ObjectType.LINE

    start: str = Field(min_length=1)

    end: str = Field(min_length=1)


class ArrowObject(AnimationObject):
    """Arrow connecting two existing objects."""

    object_type: ObjectType = ObjectType.ARROW

    start: str = Field(min_length=1)

    end: str = Field(min_length=1)
