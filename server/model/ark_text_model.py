"""创建火山模型 文本系列的"""

import json
from typing import Any
from arkruntime import Ark

from server.prompts import (
    CHARACTER_PROMPT,
    SCENE_PROMPT,
    STORY_PROMPT,
    STORYBOARD_PROMPT,
    SYSTEM_PROMPT,
)
from server.schema import (
    CharacterList,
    CharacterProfile,
    CreativeRequirement,
    SceneList,
    SceneProfile,
    StoryOutline,
    Storyboard,
    StoryBoardList,
)


class ArkTextModel:
    """火山方舟结构化输出适配器。"""

    def __init__(self, *, api_key: str, model: str) -> None:
        self._client = Ark.volc(api_key=api_key)
        self._model = model

    def _parse(self, *, system: str, payload: dict[str, Any], schema: type[Any]) -> Any:
        """各策划调用共用第 04 篇验证过的结构化输出方式。"""
        completion = self._client.beta.chat.completions.parse(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            response_format=schema,
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise ValueError("文本模型没有返回可解析的策划结果")
        return parsed

    def analyze_requirement(self, raw_requirement: str) -> CreativeRequirement:
        completion = self._client.beta.chat.completions.parse(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": raw_requirement},
            ],
            response_format=CreativeRequirement,
        )
        requirement = completion.choices[0].message.parsed
        if requirement is None:
            raise ValueError("文本模型没有返回可解析的结构化需求")
        return requirement

    def generate_story_outline(self, requirement: CreativeRequirement) -> StoryOutline:
        return self._parse(
            system=STORY_PROMPT,
            payload={"requirement": requirement.model_dump(mode="json")},
            schema=StoryOutline,
        )

    def generate_characters(
        self, requirement: CreativeRequirement, outline: StoryOutline
    ) -> list[CharacterProfile]:
        result = self._parse(
            system=CHARACTER_PROMPT,
            payload={
                "requirement": requirement.model_dump(mode="json"),
                "story_outline": outline.model_dump(mode="json"),
            },
            schema=CharacterList,
        )
        return result.characters

    def generate_scenes(
        self, requirement: CreativeRequirement, outline: StoryOutline
    ) -> list[SceneProfile]:
        result = self._parse(
            system=SCENE_PROMPT,
            payload={
                "requirement": requirement.model_dump(mode="json"),
                "story_outline": outline.model_dump(mode="json"),
            },
            schema=SceneList,
        )
        return result.scenes

    def generate_storyboard(
        self,
        requirement: CreativeRequirement,
        outline: StoryOutline,
        characters: list[CharacterProfile],
        scenes: list[SceneProfile],
    ) -> list[Storyboard]:
        result = self._parse(
            system=STORYBOARD_PROMPT,
            payload={
                # 把硬性约束从长对象里提出来置顶，减少模型在数值合计与封闭 ID 引用上的漂移
                "target_shot_count": requirement.shot_count,
                "target_duration_seconds": requirement.duration_seconds,
                "allowed_character_ids": [character.character_id for character in characters],
                "allowed_scene_ids": [scene.scene_id for scene in scenes],
                "requirement": requirement.model_dump(mode="json"),
                "story_outline": outline.model_dump(mode="json"),
                "characters": [character.model_dump(mode="json") for character in characters],
                "scenes": [scene.model_dump(mode="json") for scene in scenes],
            },
            schema=StoryBoardList,
        )
        return result.storyboard_list
