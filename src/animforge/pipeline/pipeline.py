from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from animforge.codegen import (
    CodeWriter,
    ManimCodeGenerator,
)
from animforge.dynamic import (
    DynamicCodeBridge,
)
from animforge.dynamic.source_injector import (
    DynamicSourceInjector,
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

    Static commands are handled by the existing parser.

    Dynamic commands are automatically detected and handled
    by DynamicCodeBridge.
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

        self.dynamic_bridge = (
            DynamicCodeBridge()
        )

        self.writer = (
            CodeWriter()
        )

        self.renderer = (
            ManimRenderer(
                quality=quality
            )
        )

    def _split_dynamic_commands(
        self,
        prompt: str,
    ) -> tuple[str, list[str]]:
        """
        Split a prompt into static and dynamic commands.

        The first line is always the SCENE declaration.

        Dynamic commands are detected through the dynamic bridge.

        Static commands remain untouched.
        """

        lines = [
            line.strip()
            for line in prompt.splitlines()
            if line.strip()
        ]

        if not lines:
            return prompt, []

        scene_line = lines[0]

        static_lines = [
            scene_line
        ]

        dynamic_lines: list[str] = []

        for line in lines[1:]:

            if self.dynamic_bridge.can_generate(
                line
            ):
                dynamic_lines.append(
                    line
                )

            else:
                static_lines.append(
                    line
                )

        static_prompt = "\n".join(
            static_lines
        )

        return (
            static_prompt,
            dynamic_lines,
        )

    def run(
        self,
        prompt: str,
        duration: float | None = None,
    ) -> PipelineResult:
        """
        Run the complete prompt-to-video pipeline.

        Args:
            prompt:
                AnimForge animation prompt.

            duration:
                Optional minimum target duration in seconds.

                If supplied, the generated Manim scene is extended
                with a final self.wait() so the rendered video is
                at least this duration.

        Returns:
            PipelineResult containing generated source and video paths.
        """

        # -------------------------------------------------
        # 1. Separate static and dynamic commands.
        # -------------------------------------------------

        (
            static_prompt,
            dynamic_lines,
        ) = self._split_dynamic_commands(
            prompt
        )

        # -------------------------------------------------
        # 2. Parse static scene.
        # -------------------------------------------------

        scene = (
            self.parser.parse(
                static_prompt
            )
        )

        # -------------------------------------------------
        # 3. Validate static scene.
        # -------------------------------------------------

        self.validator.validate(
            scene
        )

        # -------------------------------------------------
        # 4. Generate static Manim source.
        # -------------------------------------------------

        source = (
            self.generator.generate(
                scene
            )
        )

        # -------------------------------------------------
        # 5. Generate dynamic Manim code.
        # -------------------------------------------------

        dynamic_code: list[str] = []

        for line in dynamic_lines:

            code = (
                self.dynamic_bridge.generate(
                    line
                )
            )

            if code is None:
                continue

            dynamic_code.extend(
                code
            )

        # -------------------------------------------------
        # 6. Inject dynamic objects.
        # -------------------------------------------------

        source = (
            DynamicSourceInjector.inject(
                source,
                dynamic_code,
            )
        )

        # -------------------------------------------------
        # 7. Add duration extension.
        # -------------------------------------------------

        if duration is not None:

            if duration <= 0:
                raise ValueError(
                    "Duration must be greater than zero."
                )

            source = (
                self._add_duration_wait(
                    source,
                    duration,
                )
            )

        # -------------------------------------------------
        # 8. Determine generated class name.
        # -------------------------------------------------

        class_name = (
            self.generator._class_name(
                scene.name
            )
        )

        # -------------------------------------------------
        # 9. Determine source file.
        # -------------------------------------------------

        source_file = (
            self.output_dir
            / f"{class_name}.py"
        )

        # -------------------------------------------------
        # 10. Write final source.
        # -------------------------------------------------

        self.writer.write(
            source,
            source_file,
        )

        # -------------------------------------------------
        # 11. Render final Manim scene.
        # -------------------------------------------------

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

    @staticmethod
    def _add_duration_wait(
        source: str,
        duration: float,
    ) -> str:
        """
        Add a final self.wait() to reach the requested
        minimum video duration.

        This method estimates the duration already consumed
        by generated self.play() calls.

        The final wait is inserted before the end of
        construct().
        """

        import re

        play_durations = re.findall(
            r"run_time\s*=\s*([0-9]+(?:\.[0-9]+)?)",
            source,
        )

        elapsed = sum(
            float(value)
            for value in play_durations
        )

        remaining = (
            float(duration)
            - elapsed
        )

        if remaining <= 0:
            return source

        lines = source.splitlines()

        # Find the last line inside construct().
        # Generated Manim code places animation calls
        # near the end of construct().
        insertion_index = len(lines)

        for index in range(
            len(lines) - 1,
            -1,
            -1,
        ):
            if lines[index].strip():

                insertion_index = (
                    index + 1
                )

                break

        lines[
            insertion_index:insertion_index
        ] = [
            "",
            "        # Duration extension",
            f"        self.wait({remaining:.3f})",
        ]

        return "\n".join(
            lines
        )
