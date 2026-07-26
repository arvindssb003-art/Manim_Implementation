from animforge.codegen import ManimCodeGenerator
from animforge.models import ObjectType, Position, PolygonObject, Scene
from animforge.parser import PromptParser


def test_parse_polygon():
    prompt = """
    SCENE: Polygon Test

    POLYGON hexagon: blue at center

    ANIMATE hexagon: grow
    """

    scene = PromptParser().parse(prompt)

    polygon = scene.objects[0]

    assert isinstance(polygon, PolygonObject)
    assert polygon.id == "hexagon"
    assert polygon.object_type == ObjectType.POLYGON
    assert polygon.color == "blue"
    assert polygon.position == Position.CENTER
    assert polygon.sides == 6
    assert polygon.radius == 1.0


def test_generate_polygon_code():
    prompt = """
    SCENE: Polygon Test

    POLYGON hexagon: blue at center

    ANIMATE hexagon: grow
    """

    scene = PromptParser().parse(prompt)

    source = ManimCodeGenerator().generate(scene)

    assert "RegularPolygon" in source
    assert "n=6" in source
    assert "radius=1.0" in source
    assert "set_color(BLUE)" in source
    assert "move_to(ORIGIN)" in source
    assert "GrowFromCenter(hexagon_obj)" in source


def test_parse_polygon_relative_position():
    prompt = """
    SCENE: Polygon Relative Test

    TEXT title: "Polygon" at top
    POLYGON hexagon: blue below title
    """

    scene = PromptParser().parse(prompt)

    polygon = scene.objects[1]

    assert isinstance(polygon, PolygonObject)
    assert polygon.id == "hexagon"
    assert polygon.color == "blue"
    assert polygon.relative_position is not None
    assert polygon.relative_position.target == "title"
    assert polygon.relative_position.relation.value == "below"
