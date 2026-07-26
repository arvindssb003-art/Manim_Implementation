from __future__ import annotations

import subprocess
from pathlib import Path


class RenderError(RuntimeError):
    """Raised when Manim rendering fails."""


class ManimRenderer:
    """
    Render generated Manim Python source files.

    This class invokes the Manim CLI as a subprocess.
    It does not execute generated Python directly.
    """

    def __init__(
        self,
        quality: str = "l",
    ) -> None:
        """
        Initialize the renderer.

        Args:
            quality:
                Manim quality flag.

                Supported values:
                    l = low
                    m = medium
                    h = high
                    p = 1440p
                    k = 4K
        """

        if quality not in {
            "l",
            "m",
            "h",
            "p",
            "k",
        }:
            raise ValueError(
                "Unsupported Manim quality: "
                f"'{quality}'."
            )

        self.quality = quality

    def render(
        self,
        source_file: str | Path,
        scene_name: str,
        output_dir: str | Path = "media",
    ) -> Path:
        """
        Render a Manim scene.

        Args:
            source_file:
                Path to generated Manim Python file.

            scene_name:
                Name of the Manim Scene class.

            output_dir:
                Directory where Manim should store output.

        Returns:
            Path to the rendered MP4.

        Raises:
            RenderError:
                If rendering fails or output cannot be found.
        """

        source_path = Path(
            source_file
        ).resolve()

        output_path = Path(
            output_dir
        ).resolve()

        if not source_path.exists():
            raise RenderError(
                f"Manim source file does not exist: "
                f"{source_path}"
            )

        if source_path.suffix != ".py":
            raise RenderError(
                "Manim source file must have "
                "a .py extension."
            )

        output_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        command = [
            "manim",
            f"-q{self.quality}",
            "--media_dir",
            str(output_path),
            str(source_path),
            scene_name,
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )

        except FileNotFoundError as exc:
            raise RenderError(
                "Manim executable was not found. "
                "Make sure Manim is installed "
                "inside the active virtual environment."
            ) from exc

        if result.returncode != 0:
            raise RenderError(
                self._build_error_message(
                    result
                )
            )

        video_path = (
            self._find_rendered_video(
                output_path,
                scene_name,
            )
        )

        if video_path is None:
            raise RenderError(
                "Manim completed successfully, "
                "but the rendered MP4 could not "
                "be located."
            )

        return video_path

    @staticmethod
    def _find_rendered_video(
        media_dir: Path,
        scene_name: str,
    ) -> Path | None:
        """
        Find the rendered MP4.

        Searches recursively because Manim's output
        directory depends on the selected quality.
        """

        candidates = list(
            media_dir.rglob(
                f"{scene_name}.mp4"
            )
        )

        if not candidates:
            return None

        candidates.sort(
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        return candidates[0]

    @staticmethod
    def _build_error_message(
        result: subprocess.CompletedProcess[str],
    ) -> str:
        """Build a useful rendering error message."""

        stderr = (
            result.stderr.strip()
            if result.stderr
            else ""
        )

        stdout = (
            result.stdout.strip()
            if result.stdout
            else ""
        )

        details = stderr or stdout

        if not details:
            details = (
                "Manim exited with "
                f"return code {result.returncode}."
            )

        return (
            "Manim rendering failed.\n\n"
            f"{details}"
        )