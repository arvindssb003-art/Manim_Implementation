from pathlib import Path

import pytest

from animforge.render import (
    ManimRenderer,
    RenderError,
)


def test_renderer_accepts_valid_quality():
    renderer = ManimRenderer(
        quality="l"
    )

    assert renderer.quality == "l"


def test_renderer_rejects_invalid_quality():
    with pytest.raises(
        ValueError,
        match="Unsupported Manim quality",
    ):
        ManimRenderer(
            quality="x"
        )


def test_renderer_requires_python_file(
    tmp_path: Path,
):
    source_file = (
        tmp_path
        / "scene.txt"
    )

    source_file.write_text(
        "invalid",
        encoding="utf-8",
    )

    renderer = ManimRenderer()

    with pytest.raises(
        RenderError,
        match=".py extension",
    ):
        renderer.render(
            source_file,
            "TestScene",
        )


def test_renderer_requires_existing_file(
    tmp_path: Path,
):
    source_file = (
        tmp_path
        / "missing.py"
    )

    renderer = ManimRenderer()

    with pytest.raises(
        RenderError,
        match="does not exist",
    ):
        renderer.render(
            source_file,
            "TestScene",
        )


def test_find_rendered_video(
    tmp_path: Path,
):
    video_dir = (
        tmp_path
        / "videos"
        / "480p15"
    )

    video_dir.mkdir(
        parents=True
    )

    video_file = (
        video_dir
        / "TestScene.mp4"
    )

    video_file.write_bytes(
        b"fake video"
    )

    result = (
        ManimRenderer
        ._find_rendered_video(
            tmp_path,
            "TestScene",
        )
    )

    assert result == video_file


def test_find_rendered_video_returns_none(
    tmp_path: Path,
):
    result = (
        ManimRenderer
        ._find_rendered_video(
            tmp_path,
            "MissingScene",
        )
    )

    assert result is None