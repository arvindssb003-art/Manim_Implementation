from __future__ import annotations

import re


class DynamicSourceInjector:
    """
    Inject dynamically generated Manim object code into
    an existing generated Manim source.

    Static code generation remains untouched.

    Dynamic object code is inserted after static object
    creation and before existing animation calls.

    If the generated scene has no animation calls, this
    injector automatically creates a Create(...) animation
    for the dynamically generated objects.
    """

    @staticmethod
    def inject(
        source: str,
        dynamic_lines: list[str],
    ) -> str:
        """
        Inject dynamic object code into generated source.

        Args:
            source:
                Existing generated Manim source.

            dynamic_lines:
                Generated dynamic object code.

        Returns:
            Updated Manim source.
        """

        if not dynamic_lines:
            return source

        lines = source.splitlines()

        # -----------------------------------------------------
        # Extract dynamic object variable names.
        #
        # Example:
        #
        #   arc1_obj = Arc(...)
        #
        #   parabola_obj = FunctionGraph(...)
        #
        # becomes:
        #
        #   ["arc1_obj", "parabola_obj"]
        # -----------------------------------------------------

        dynamic_objects = (
            DynamicSourceInjector._extract_object_variables(
                dynamic_lines
            )
        )

        # -----------------------------------------------------
        # Find the first animation call.
        #
        # Dynamic object creation should happen before
        # existing animations.
        # -----------------------------------------------------

        animation_index = (
            DynamicSourceInjector._find_first_animation(
                lines
            )
        )

        # -----------------------------------------------------
        # Build the dynamic object creation block.
        # -----------------------------------------------------

        generated = [
            "",
            "        # Dynamic objects",
            "",
        ]

        generated.extend(
            (
                f"        {line}"
                if line.strip()
                else ""
            )
            for line in dynamic_lines
        )

        generated.append("")

        # -----------------------------------------------------
        # If existing animations are present:
        #
        #   static objects
        #   dynamic objects
        #   existing animations
        #
        # Insert dynamic Create animations immediately
        # before the existing animation sequence.
        # -----------------------------------------------------

        if animation_index is not None:

            animation_block = (
                DynamicSourceInjector
                ._build_create_animation(
                    dynamic_objects
                )
            )

            if animation_block:
                generated.extend(
                    animation_block
                )

                generated.append("")

            lines[
                animation_index:animation_index
            ] = generated

            return "\n".join(
                lines
            )

        # -----------------------------------------------------
        # No existing animation calls.
        #
        # The old injector simply appended object creation,
        # resulting in:
        #
        #   Played 0 animations
        #
        # Manim then produced a PNG instead of an MP4.
        #
        # We now add:
        #
        #   self.play(
        #       Create(arc1_obj),
        #       Create(parabola_obj),
        #   )
        #
        # This guarantees the dynamic objects are rendered
        # as an animation.
        # -----------------------------------------------------

        animation_block = (
            DynamicSourceInjector
            ._build_create_animation(
                dynamic_objects
            )
        )

        if animation_block:
            generated.extend(
                animation_block
            )

            generated.append("")

        # -----------------------------------------------------
        # Find the end of construct().
        #
        # We insert before the final method/class boundary
        # rather than blindly appending after the entire file.
        # -----------------------------------------------------

        insertion_index = (
            DynamicSourceInjector
            ._find_construct_end(
                lines
            )
        )

        lines[
            insertion_index:insertion_index
        ] = generated

        return "\n".join(
            lines
        )

    @staticmethod
    def _extract_object_variables(
        dynamic_lines: list[str],
    ) -> list[str]:
        """
        Extract generated Manim object variable names.

        Example:

            arc1_obj = Arc(...)
            parabola_obj = FunctionGraph(...)

        Returns:

            ["arc1_obj", "parabola_obj"]
        """

        variables: list[str] = []

        assignment_pattern = re.compile(
            r"^\s*"
            r"(?P<variable>[A-Za-z_][A-Za-z0-9_]*)"
            r"\s*="
        )

        for line in dynamic_lines:

            match = assignment_pattern.match(
                line
            )

            if not match:
                continue

            variable = (
                match.group(
                    "variable"
                )
            )

            # Only treat generated object variables
            # as animation targets.
            #
            # Current dynamic features convention:
            #
            #   <object_id>_obj
            #
            if not variable.endswith(
                "_obj"
            ):
                continue

            if variable not in variables:
                variables.append(
                    variable
                )

        return variables

    @staticmethod
    def _find_first_animation(
        lines: list[str],
    ) -> int | None:
        """
        Find the first existing animation call.

        Detects:

            self.play(...)

            self.wait(...)

        Returns:
            Line index or None.
        """

        for index, line in enumerate(
            lines
        ):
            stripped = line.strip()

            if (
                stripped.startswith(
                    "self.play("
                )
                or stripped.startswith(
                    "self.wait("
                )
            ):
                return index

        return None

    @staticmethod
    def _build_create_animation(
        object_variables: list[str],
    ) -> list[str]:
        """
        Build a Manim Create animation block.

        Example:

            self.play(
                Create(arc1_obj),
                Create(parabola_obj),
            )
        """

        if not object_variables:
            return []

        lines = [
            "        self.play(",
        ]

        for index, variable in enumerate(
            object_variables
        ):
            suffix = (
                ","
                if index
                < len(object_variables) - 1
                else ""
            )

            lines.append(
                f"            Create({variable})"
                f"{suffix}"
            )

        lines.append(
            "        )"
        )

        return lines

    @staticmethod
    def _find_construct_end(
        lines: list[str],
    ) -> int:
        """
        Find the insertion point at the end of construct().

        The generated source generally looks like:

            class DemoScene(Scene):

                def construct(self):

                    ...

        We insert dynamic code before the next top-level
        class/function definition or at the end of the file.
        """

        construct_index = None

        for index, line in enumerate(
            lines
        ):
            if line.strip().startswith(
                "def construct("
            ):
                construct_index = index
                break

        if construct_index is None:
            return len(lines)

        # Search for the next top-level definition.
        #
        # A line with no indentation beginning with
        # "class " or "def " marks the end of construct().
        for index in range(
            construct_index + 1,
            len(lines),
        ):
            line = lines[index]

            if not line.strip():
                continue

            if (
                not line.startswith(
                    " "
                )
                and not line.startswith(
                    "\t"
                )
            ):
                if (
                    line.startswith(
                        "class "
                    )
                    or line.startswith(
                        "def "
                    )
                ):
                    return index

        return len(lines)