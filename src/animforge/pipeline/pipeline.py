from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from animforge.codegen import (
    CodeWriter,
    ManimCodeGenerator,
)
from animforge.parser import PromptParser
from animforge.render import ManimRenderer
from animforge.validation import SceneValidator


@dataclass(frozen=True)
class PipelineResult:
    """
    Result produced by the AnimForge pipeline.
    """

    scene_name: str
    class_name: str
    source_file: Path
    video_file: Path


class AnimationPipeline:
    """
    Run the complete prompt-to-video pipeline.

    Flow:

        Prompt
            ↓
        Parser
            ↓
        Validator
            ↓
        Code Generator
            ↓
        Code Writer
            ↓
        Manim Renderer
            ↓
        MP4
    """

    def __init__(
        self,
        output_dir: str | Path = "generated",
        media_dir: str | Path = "media",
        quality: str = "l",
    ) -> None:

        self.output_dir = Path(
            output_dir
        )

        self.media_dir = Path(
            media_dir
        )

        self.parser = PromptParser()

        self.validator = (
            SceneValidator()
        )

        self.generator = (
            ManimCodeGenerator()
        )

        self.writer = (
            CodeWriter()
        )

        self.renderer = (
            ManimRenderer(
                quality=quality
            )
        )

    def run(
        self,
        prompt: str,
    ) -> PipelineResult:
        """
        Run the complete pipeline.

        Args:
            prompt:
                Supported AnimForge prompt.

        Returns:
            PipelineResult containing generated
            source and video paths.
        """

        scene = (
            self.parser.parse(
                prompt
            )
        )

        self.validator.validate(
            scene
        )

        source = (
            self.generator.generate(
                scene
            )
        )

        class_name = (
            self.generator._class_name(
                scene.name
            )
        )

        source_file = (
            self.output_dir
            / f"{class_name}.py"
        )

        self.writer.write(
            source,
            source_file,
        )

        video_file = (
            self.renderer.render(
                source_file,
                class_name,
                self.media_dir,
            )
        )

        return PipelineResult(
            scene_name=scene.name,
            class_name=class_name,
            source_file=source_file,
            video_file=video_file,
        )