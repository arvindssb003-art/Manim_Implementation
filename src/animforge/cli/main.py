from __future__ import annotations

import argparse
import sys
from pathlib import Path

from animforge.pipeline import AnimationPipeline


def build_parser() -> argparse.ArgumentParser:
    """
    Build the AnimForge command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        prog="animforge",
        description=(
            "AnimForge - Convert supported animation "
            "prompts into Manim videos."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate a Manim video from a prompt.",
    )

    input_group = generate_parser.add_mutually_exclusive_group(
        required=True,
    )

    input_group.add_argument(
        "--prompt",
        type=str,
        help="Animation prompt provided directly.",
    )

    input_group.add_argument(
        "--prompt-file",
        type=Path,
        help="Path to a text file containing the prompt.",
    )

    generate_parser.add_argument(
        "--quality",
        choices=[
            "l",
            "m",
            "h",
            "p",
            "k",
        ],
        default="l",
        help=(
            "Manim render quality. "
            "Default: l"
        ),
    )

    generate_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("generated"),
        help=(
            "Directory for generated Python files. "
            "Default: generated"
        ),
    )

    generate_parser.add_argument(
        "--media-dir",
        type=Path,
        default=Path("media"),
        help=(
            "Directory for rendered videos. "
            "Default: media"
        ),
    )

    return parser


def read_prompt(
    args: argparse.Namespace,
) -> str:
    """
    Read the prompt from CLI arguments.
    """

    if args.prompt is not None:
        prompt = args.prompt

    elif args.prompt_file is not None:
        prompt_file: Path = (
            args.prompt_file
        )

        if not prompt_file.exists():
            raise FileNotFoundError(
                f"Prompt file does not exist: "
                f"{prompt_file}"
            )

        if not prompt_file.is_file():
            raise ValueError(
                f"Prompt path is not a file: "
                f"{prompt_file}"
            )

        prompt = prompt_file.read_text(
            encoding="utf-8"
        )

    else:
        raise ValueError(
            "Either --prompt or "
            "--prompt-file is required."
        )

    if not prompt.strip():
        raise ValueError(
            "Prompt cannot be empty."
        )

    return prompt


def run_generate(
    args: argparse.Namespace,
) -> int:
    """
    Run the generate command.
    """

    try:
        prompt = read_prompt(args)

        print(
            "\n[1/5] Parsing prompt..."
        )

        pipeline = AnimationPipeline(
            output_dir=args.output_dir,
            media_dir=args.media_dir,
            quality=args.quality,
        )

        print(
            "[2/5] Validating scene..."
        )

        print(
            "[3/5] Generating Manim code..."
        )

        print(
            "[4/5] Rendering Manim scene..."
        )

        result = pipeline.run(
            prompt
        )

        print(
            "[5/5] Generation complete."
        )

        print()
        print(
            "Scene:",
            result.scene_name,
        )

        print(
            "Python:",
            result.source_file,
        )

        print(
            "Video:",
            result.video_file,
        )

        return 0

    except Exception as exc:
        print(
            "\nAnimForge generation failed:",
            file=sys.stderr,
        )

        print(
            str(exc),
            file=sys.stderr,
        )

        return 1


def main() -> int:
    """
    CLI application entry point.
    """

    parser = build_parser()

    args = parser.parse_args()

    if args.command == "generate":
        return run_generate(args)

    parser.print_help()

    return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )