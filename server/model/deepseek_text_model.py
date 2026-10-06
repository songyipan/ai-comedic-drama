"""DeepSeek 文本模型。用 LangChain 的 provider 选择接口，并直接做结构化输出。"""

import json
from typing import Any

from langchain.chat_models import init_chat_model

from server.prompts.planning_graph import (
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

# DeepSeek 同时提供这两套兼容接口，由 DEEPSEEK_MODEL_PROVIDER 选择。
DEEPSEEK_BASE_URLS = {
    "openai": "https://api.deepseek.com",
    "anthropic": "https://api.deepseek.com/anthropic",
}


class DeepSeekTextModel:
    """把策划步骤的 Pydantic 契约交给 DeepSeek，节点不接触厂商 SDK。"""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        model_provider: str = "",
        chat_model: Any | None = None,
    ) -> None:
        if chat_model is None:
            provider = model_provider.strip().lower()
            base_url = DEEPSEEK_BASE_URLS.get(provider)
            if base_url is None:
                allowed = "、".join(DEEPSEEK_BASE_URLS)
                raise ValueError(
                    f"不支持的 DEEPSEEK_MODEL_PROVIDER：{model_provider}。可选值为 {allowed}"
                )
            # DeepSeek 默认开着思考模式，这时不接受结构化输出用的 tool_choice。
            provider_kwargs: dict[str, Any] = {"max_tokens": 8192}
            if provider == "openai":
                provider_kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
            else:
                provider_kwargs["thinking"] = {"type": "disabled"}
            chat_model = init_chat_model(
                model,
                model_provider=provider,
                api_key=api_key,
                base_url=base_url,
                **provider_kwargs,
            )
        self._chat = chat_model

    def _invoke(
        self,
        *,
        system: str,
        user_content: str,
        schema: type[Any],
        empty_message: str,
    ) -> Any:
        # function_calling 会在这一次调用内部塞一个临时 tool，解析后只返回 Pydantic 对象。
        parsed = self._chat.with_structured_output(schema, method="function_calling").invoke(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ]
        )
        if parsed is None:
            raise ValueError(empty_message)
        return parsed

    def _parse(self, *, system: str, payload: dict[str, Any], schema: type[Any]) -> Any:
        return self._invoke(
            system=system,
            user_content=json.dumps(payload, ensure_ascii=False),
            schema=schema,
            empty_message="文本模型没有返回可解析的策划结果",
        )

    def analyze_requirement(self, raw_requirement: str) -> CreativeRequirement:
        return self._invoke(
            system=SYSTEM_PROMPT,
            user_content=raw_requirement,
            schema=CreativeRequirement,
            empty_message="文本模型没有返回可解析的结构化需求",
        )

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
