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

        # -----------------------------------------------------
        # Capture the state of MP4 files before rendering.
        #
        # This lets us identify the file created by this
        # specific render, even if Manim changes its output
        # directory structure.
        # -----------------------------------------------------

        before_files = {
            path.resolve()
            for path in output_path.rglob(
                "*.mp4"
            )
            if path.is_file()
        }

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

        # -----------------------------------------------------
        # First try the exact expected scene filename.
        # -----------------------------------------------------

        video_path = (
            self._find_rendered_video(
                output_path,
                scene_name,
            )
        )

        if video_path is not None:
            return video_path

        # -----------------------------------------------------
        # If the exact filename was not found, look for newly
        # created MP4 files.
        # -----------------------------------------------------

        new_files = [
            path
            for path in output_path.rglob(
                "*.mp4"
            )
            if path.is_file()
            and path.resolve()
            not in before_files
        ]

        if new_files:
            new_files.sort(
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )

            return new_files[0]

        # -----------------------------------------------------
        # Final fallback:
        #
        # Search all MP4 files and choose the newest one.
        #
        # This handles cases where Manim overwrites an existing
        # scene file instead of creating a new inode.
        # -----------------------------------------------------

        all_files = [
            path
            for path in output_path.rglob(
                "*.mp4"
            )
            if path.is_file()
        ]

        if all_files:
            all_files.sort(
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )

            newest = all_files[0]

            # Only accept a recent file. This prevents returning
            # an unrelated old render if this render produced
            # nothing.
            if self._is_recent(
                newest,
                seconds=30,
            ):
                return newest

        raise RenderError(
            self._build_missing_video_message(
                output_path,
                scene_name,
                result,
            )
        )

    @staticmethod
    def _find_rendered_video(
        media_dir: Path,
        scene_name: str,
    ) -> Path | None:
        """
        Find the exact rendered scene MP4.

        Searches recursively because Manim's output
        directory depends on the selected quality.
        """

        candidates = list(
            media_dir.rglob(
                f"{scene_name}.mp4"
            )
        )

        candidates = [
            path
            for path in candidates
            if path.is_file()
            and "partial_movie_files"
            not in path.parts
        ]

        if not candidates:
            return None

        candidates.sort(
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        return candidates[0]

    @staticmethod
    def _is_recent(
        path: Path,
        seconds: int = 30,
    ) -> bool:
        """
        Return True if a file was modified recently.
        """

        import time

        age = (
            time.time()
            - path.stat().st_mtime
        )

        return age <= seconds

    @staticmethod
    def _build_missing_video_message(
        media_dir: Path,
        scene_name: str,
        result: subprocess.CompletedProcess[str],
    ) -> str:
        """
        Build a detailed error when Manim exits successfully
        but no final MP4 can be located.
        """

        mp4_files = sorted(
            str(path)
            for path in media_dir.rglob(
                "*.mp4"
            )
            if path.is_file()
        )

        stdout = (
            result.stdout.strip()
            if result.stdout
            else ""
        )

        stderr = (
            result.stderr.strip()
            if result.stderr
            else ""
        )

        message = [
            "Manim completed successfully, "
            "but the rendered MP4 could not "
            "be located.",
            "",
            f"Scene: {scene_name}",
            f"Media directory: {media_dir}",
        ]

        if mp4_files:
            message.extend(
                [
                    "",
                    "MP4 files currently found:",
                    *mp4_files,
                ]
            )
        else:
            message.extend(
                [
                    "",
                    "No MP4 files were found "
                    "under the media directory.",
                ]
            )

        if stdout:
            message.extend(
                [
                    "",
                    "Manim stdout:",
                    stdout,
                ]
            )

        if stderr:
            message.extend(
                [
                    "",
                    "Manim stderr:",
                    stderr,
                ]
            )

        return "\n".join(
            message
        )

    @staticmethod
    def _build_error_message(
        result: subprocess.CompletedProcess[str],
    ) -> str:
        """
        Build a useful rendering error message.
        """

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