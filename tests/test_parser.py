from animforge.models import AnimationType, Position
from animforge.parser import ParserError, PromptParser


def test_parse_basic_scene():
    prompt = """
    SCENE: Neural Network

    TEXT title: "Neural Networks" at top
    CIRCLE input: blue at center
    RECTANGLE output: red at bottom

    ANIMATE title: write
    ANIMATE input: grow
    ANIMATE output: fade_in
    """

    parser = PromptParser()
    scene = parser.parse(prompt)

    assert scene.name == "Neural Network"

    assert len(scene.objects) == 3
    assert len(scene.animations) == 3

    assert scene.objects[0].id == "title"
    assert scene.objects[0].position == Position.TOP

    assert scene.objects[1].id == "input"
    assert scene.objects[1].color == "blue"

    assert scene.animations[0].target == "title"
    assert scene.animations[0].animation_type == AnimationType.WRITE


def test_parse_text():
    prompt = """
    SCENE: Test

    TEXT title: "Hello World" at center
    """

    scene = PromptParser().parse(prompt)

    title = scene.objects[0]

    assert title.id == "title"
    assert title.content == "Hello World"
    assert title.position == Position.CENTER


def test_parse_invalid_animation():
    prompt = """
    SCENE: Test

    CIRCLE circle: blue at center
    ANIMATE circle: bounce
    """

    parser = PromptParser()

    try:
        parser.parse(prompt)
        assert False, "Expected ParserError"
    except ParserError as exc:
        assert "Unsupported animation" in str(exc)


def test_parse_empty_prompt():
    parser = PromptParser()

    try:
        parser.parse("")
        assert False, "Expected ParserError"
    except ParserError as exc:
        assert "empty" in str(exc).lower()


def test_parse_unknown_command():
    prompt = """
    SCENE: Test

    UNKNOWN something
    """

    parser = PromptParser()

    try:
        parser.parse(prompt)
        assert False, "Expected ParserError"
    except ParserError as exc:
        assert "Unsupported command" in str(exc)


def test_parse_relative_positions():
    prompt = """
    SCENE: Neural Network

    TEXT title: "Neural Networks" at top
    CIRCLE input: blue below title
    RECTANGLE output: red below input

    ANIMATE title: write
    ANIMATE input: grow
    ANIMATE output: fade_in
    """

    scene = PromptParser().parse(prompt)

    title = scene.get_object("title")
    input_node = scene.get_object("input")
    output = scene.get_object("output")

    assert title.position == Position.TOP

    assert input_node.relative_position is not None
    assert input_node.relative_position.target == "title"

    assert (
        input_node.relative_position.relation.value
        == "below"
    )

    assert output.relative_position is not None
    assert output.relative_position.target == "input"