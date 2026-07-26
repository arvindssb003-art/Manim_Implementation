from animforge.models import (
    Animation,
    AnimationType,
    CircleObject,
    Position,
    Scene,
    TextObject,
)


def test_create_scene():
    scene = Scene(name="Neural Network")

    title = TextObject(
        id="title",
        content="Neural Networks",
        position=Position.TOP,
    )

    circle = CircleObject(
        id="circle",
        position=Position.CENTER,
        color="blue",
    )

    animation = Animation(
        target="title",
        animation_type=AnimationType.WRITE,
        duration=2.0,
    )

    scene.add_object(title)
    scene.add_object(circle)
    scene.add_animation(animation)

    assert scene.name == "Neural Network"
    assert len(scene.objects) == 2
    assert len(scene.animations) == 1

    assert scene.get_object("title").id == "title"
    assert scene.get_object("circle").id == "circle"
