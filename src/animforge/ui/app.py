from __future__ import annotations

from pathlib import Path

import streamlit as st

from animforge.pipeline import AnimationPipeline


st.set_page_config(
    page_title="AnimForge",
    page_icon="🎬",
    layout="wide",
)


def main() -> None:
    st.title("🎬 AnimForge")
    st.caption(
        "Convert animation prompts into Manim videos."
    )

    st.subheader("Animation Prompt")

    prompt = st.text_area(
        "Enter your animation prompt",
        height=300,
        placeholder=(
            "SCENE: Polygon Demo\n"
            "\n"
            "TEXT title: \"Polygon Demo\" at top\n"
            "POLYGON hexagon: blue at center\n"
            "\n"
            "ANIMATE title: write\n"
            "ANIMATE hexagon: grow"
        ),
    )

    quality = st.selectbox(
        "Render Quality",
        options=[
            "l",
            "m",
            "h",
            "p",
            "k",
        ],
        index=0,
        format_func=lambda value: {
            "l": "Low - Fast Preview",
            "m": "Medium",
            "h": "High",
            "p": "Production",
            "k": "4K",
        }[value],
    )

    generate_button = st.button(
        "🎬 Generate Animation",
        type="primary",
        use_container_width=True,
    )

    if not generate_button:
        return

    if not prompt.strip():
        st.warning(
            "Please enter an animation prompt."
        )
        return

    try:
        with st.status(
            "Generating animation...",
            expanded=True,
        ) as status:
            st.write(
                "Parsing and validating prompt..."
            )

            pipeline = AnimationPipeline(
                quality=quality,
            )

            st.write(
                "Generating Manim code..."
            )

            result = pipeline.run(
                prompt,
            )

            st.write(
                "Rendering Manim scene..."
            )

            status.update(
                label="Animation generated successfully!",
                state="complete",
            )

        st.success(
            f"Scene generated: "
            f"{result.scene_name}"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(
                "Generated Python"
            )

            source_path = Path(
                result.source_file
            )

            if source_path.exists():
                source = source_path.read_text(
                    encoding="utf-8"
                )

                st.code(
                    source,
                    language="python",
                )
            else:
                st.info(
                    "Generated Python file: "
                    f"{result.source_file}"
                )

        with col2:
            st.subheader(
                "Generated Video"
            )

            video_path = Path(
                result.video_file
            )

            if video_path.exists():
                st.video(
                    str(video_path)
                )

                with open(
                    video_path,
                    "rb",
                ) as video_file:
                    st.download_button(
                        label="⬇️ Download Video",
                        data=video_file,
                        file_name=video_path.name,
                        mime="video/mp4",
                    )
            else:
                st.warning(
                    "Video file was not found: "
                    f"{result.video_file}"
                )

    except Exception as exc:
        st.error(
            "Animation generation failed."
        )

        with st.expander(
            "Show error details"
        ):
            st.exception(exc)


if __name__ == "__main__":
    main()
