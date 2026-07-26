from __future__ import annotations

from pathlib import Path

from animforge.codegen.generator import (
    CodeGenerationError,
)


class CodeWriter:
    """
    Write generated Python source code to disk.
    """

    def write(
        self,
        source: str,
        output_path: str | Path,
    ) -> Path:
        """
        Write source code to a Python file.

        Args:
            source: Generated Python source code.
            output_path: Destination file path.

        Returns:
            Path to the written file.

        Raises:
            CodeGenerationError:
                If the output path is invalid or writing fails.
        """

        path = Path(output_path)

        if path.suffix != ".py":
            raise CodeGenerationError(
                "Generated Manim code must be "
                "written to a .py file."
            )

        try:
            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            path.write_text(
                source,
                encoding="utf-8",
            )

        except OSError as exc:
            raise CodeGenerationError(
                f"Failed to write generated code "
                f"to '{path}': {exc}"
            ) from exc

        return path