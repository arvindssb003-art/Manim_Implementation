import pytest

from animforge.models import (
    Animation,
    AnimationType,
    ArrowObject,
    CircleObject,
    Position,
    RelativePosition,
    RelationType,
    Scene,
)

from animforge.validation import (
    SceneValidator,
    ValidationError,
)


def test_valid_scene_passes_validation():
    scene = Scene(name="Valid Scene")

    circle = CircleObject(
        id="circle",
        position=Position.CENTER,
    )

    animation = Animation(
        target="circle",
        animation_type=AnimationType.GROW,
    )

    scene.add_object(circle)
    scene.add_animation(animation)

    SceneValidator().validate(scene)


def test_animation_target_must_exist():
    scene = Scene(name="Invalid Scene")

    circle = CircleObject(
        id="circle",
        position=Position.CENTER,
    )

    animation = Animation(
        target="missing",
        animation_type=AnimationType.GROW,
    )

    scene.add_object(circle)
    scene.add_animation(animation)

    with pytest.raises(
        ValidationError,
        match="unknown object 'missing'",
    ):
        SceneValidator().validate(scene)


def test_relative_position_target_must_exist():
    scene = Scene(name="Invalid Scene")

    circle = CircleObject(
        id="circle",
        relative_position=RelativePosition(
            relation=RelationType.BELOW,
            target="missing",
        ),
    )

    scene.add_object(circle)

    with pytest.raises(
        ValidationError,
        match="unknown object 'missing'",
    ):
        SceneValidator().validate(scene)


def test_object_cannot_reference_itself():
    scene = Scene(name="Invalid Scene")

    circle = CircleObject(
        id="circle",
        relative_position=RelativePosition(
            relation=RelationType.BELOW,
            target="circle",
        ),
    )

    scene.add_object(circle)

    with pytest.raises(
        ValidationError,
        match="cannot be positioned relative to itself",
    ):
        SceneValidator().validate(scene)


def test_arrow_references_must_exist():
    scene = Scene(name="Invalid Scene")

    # The start object exists.
    input_node = CircleObject(
        id="input",
        position=Position.CENTER,
    )

    # The end object "missing" does not exist.
    arrow = ArrowObject(
        id="connection",
        start="input",
        end="missing",
    )

    scene.add_object(input_node)
    scene.add_object(arrow)

    with pytest.raises(
        ValidationError,
        match="invalid arrow end reference",
    ):
        SceneValidator().validate(scene)


def test_circular_layout_is_rejected():
    scene = Scene(name="Circular Scene")

    first = CircleObject(
        id="first",
        relative_position=RelativePosition(
            relation=RelationType.BELOW,
            target="second",
        ),
    )

    second = CircleObject(
        id="second",
        relative_position=RelativePosition(
            relation=RelationType.BELOW,
            target="first",
        ),
    )

    scene.add_object(first)
    scene.add_object(second)

    with pytest.raises(
        ValidationError,
        match="Circular relative-position",
    ):
        SceneValidator().validate(scene)