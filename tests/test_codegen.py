from pathlib import Path

from animforge.codegen import (
    CodeGenerationError,
    CodeWriter,
    ManimCodeGenerator,
)

from animforge.models import (
    Animation,
    AnimationType,
    CircleObject,
    Position,
    RelativePosition,
    RelationType,
    Scene,
    TextObject,
)


def test_generate_empty_scene():
    scene = Scene(
        name="Empty",
    )

    source = ManimCodeGenerator().generate(
        scene
    )

    assert "from manim import *" in source
    assert "class EmptyScene(Scene):" in source
    assert "def construct(self):" in source
    assert "pass" in source


def test_generate_text():
    scene = Scene(
        name="Text Test",
    )

    title = TextObject(
        id="title",
        content="Hello World",
        position=Position.TOP,
    )

    scene.add_object(title)

    source = ManimCodeGenerator().generate(
        scene
    )

    assert (
        "title_obj = Text('Hello World')"
        in source
    )

    assert (
        "title_obj.to_edge(UP)"
        in source
    )


def test_python_keyword_is_safe():
    scene = Scene(
        name="Keyword Test",
    )

    input_circle = CircleObject(
        id="input",
        position=Position.CENTER,
    )

    scene.add_object(
        input_circle
    )

    source = ManimCodeGenerator().generate(
        scene
    )

    assert (
        "input_obj = Circle"
        in source
    )

    assert (
        "input = Circle"
        not in source
    )


def test_generate_circle():
    scene = Scene(
        name="Circle Test",
    )

    circle = CircleObject(
        id="circle",
        radius=2.0,
        color="blue",
        position=Position.CENTER,
    )

    scene.add_object(circle)

    source = ManimCodeGenerator().generate(
        scene
    )

    assert (
        "circle_obj = Circle(radius=2.0)"
        in source
    )

    assert (
        "circle_obj.set_color(BLUE)"
        in source
    )

    assert (
        "circle_obj.move_to(ORIGIN)"
        in source
    )


def test_generate_relative_position():
    scene = Scene(
        name="Relative Test",
    )

    title = TextObject(
        id="title",
        content="Neural Networks",
        position=Position.TOP,
    )

    circle = CircleObject(
        id="input",
        relative_position=RelativePosition(
            relation=RelationType.BELOW,
            target="title",
        ),
    )

    scene.add_object(title)
    scene.add_object(circle)

    source = ManimCodeGenerator().generate(
        scene
    )

    assert (
        "input_obj.next_to("
        "title_obj, DOWN)"
        in source
    )


def test_generate_animations():
    scene = Scene(
        name="Animation Test",
    )

    title = TextObject(
        id="title",
        content="Hello",
        position=Position.CENTER,
    )

    scene.add_object(title)

    scene.add_animation(
        Animation(
            target="title",
            animation_type=AnimationType.WRITE,
            duration=2.0,
        )
    )

    source = ManimCodeGenerator().generate(
        scene
    )

    assert (
        "self.play("
        "Write(title_obj), "
        "run_time=2.0)"
        in source
    )


def test_generated_code_has_valid_python_syntax():
    scene = Scene(
        name="Syntax Test",
    )

    title = TextObject(
        id="title",
        content="Hello",
    )

    scene.add_object(title)

    source = ManimCodeGenerator().generate(
        scene
    )

    ManimCodeGenerator.validate_python_syntax(
        source
    )


def test_invalid_scene_cannot_generate_code():
    scene = Scene(
        name="Invalid Scene",
    )

    scene.add_animation(
        Animation(
            target="missing",
            animation_type=AnimationType.WRITE,
        )
    )

    generator = ManimCodeGenerator()

    try:
        generator.generate(scene)

        assert False, (
            "Expected CodeGenerationError"
        )

    except CodeGenerationError as exc:
        assert (
            "invalid scene"
            in str(exc).lower()
        )


def test_code_writer_creates_python_file(
    tmp_path: Path,
):
    source = """\
from manim import *


class TestScene(Scene):

    def construct(self):
        pass
"""

    output_path = (
        tmp_path
        / "generated_scene.py"
    )

    writer = CodeWriter()

    result = writer.write(
        source,
        output_path,
    )

    assert result == output_path
    assert output_path.exists()

    content = output_path.read_text(
        encoding="utf-8"
    )

    assert (
        content == source
    )


def test_code_writer_creates_parent_directory(
    tmp_path: Path,
):
    source = "print('hello')"

    output_path = (
        tmp_path
        / "generated"
        / "scene.py"
    )

    CodeWriter().write(
        source,
        output_path,
    )

    assert output_path.exists()


def test_code_writer_requires_python_extension(
    tmp_path: Path,
):
    source = "print('hello')"

    output_path = (
        tmp_path
        / "scene.txt"
    )

    writer = CodeWriter()

    try:
        writer.write(
            source,
            output_path,
        )

        assert False, (
            "Expected CodeGenerationError"
        )

    except CodeGenerationError as exc:
        assert (
            ".py file"
            in str(exc)
        )