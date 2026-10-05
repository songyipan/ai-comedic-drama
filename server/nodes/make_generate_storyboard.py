"""make_generate_storyboard。"""

from server.model import TextModel
from server.states import ComicDramaState


def make_generate_storyboard(text_model: TextModel):
    def generate_storyboard(state: ComicDramaState) -> dict[str, object]:
        requirement = state.get("requirement")
        outline = state.get("story_outline")
        characters = state.get("characters")
        scenes = state.get("scenes")
        if requirement is None or outline is None or characters is None or scenes is None:
            raise ValueError("缺少需求、大纲、角色或场景，不能生成分镜")
        return {
            "storyboard": text_model.generate_storyboard(requirement, outline, characters, scenes),
            "events": ["已生成分镜"],
        }

    return generate_storyboard
