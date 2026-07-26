from pydantic import BaseModel, Field

from .animations import Animation
from .objects import AnimationObject


class Scene(BaseModel):
    """Represents a complete AnimForge animation scene."""

    name: str = Field(min_length=1)

    objects: list[AnimationObject] = Field(default_factory=list)

    animations: list[Animation] = Field(default_factory=list)

    def add_object(self, obj: AnimationObject) -> None:
        """Add an object to the scene."""

        if any(existing.id == obj.id for existing in self.objects):
            raise ValueError(
                f"An object with id '{obj.id}' already exists."
            )

        self.objects.append(obj)

    def add_animation(self, animation: Animation) -> None:
        """Add an animation to the scene."""

        self.animations.append(animation)

    def get_object(self, object_id: str) -> AnimationObject:
        """Return an object by its ID."""

        for obj in self.objects:
            if obj.id == object_id:
                return obj

        raise ValueError(
            f"Object '{object_id}' does not exist."
        )