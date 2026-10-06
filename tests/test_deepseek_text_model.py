"""真实文本模型用 LangChain 的 provider 参数接 DeepSeek，并直接做结构化输出。"""

import json

import pytest

from server.config.deepseek_settings import deepseek_settings
from server.config.text_model_settings import text_model_settings
from server.model.build_text_model import build_text_model
from server.model.deepseek_text_model import DeepSeekTextModel
from server.prompts.planning_graph import (
    CHARACTER_PROMPT,
    SCENE_PROMPT,
    STORY_PROMPT,
    STORYBOARD_PROMPT,
    SYSTEM_PROMPT,
)
from server.schema import (
    CharacterProfile,
    CreativeRequirement,
    SceneProfile,
    StoryOutline,
    Storyboard,
)


class RecordingStructuredChat:
    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def with_structured_output(self, schema, **kwargs):
        call = {"schema": schema, "kwargs": kwargs}
        self.calls.append(call)
        chat = self

        class Bound:
            def invoke(self, messages):
                call["messages"] = messages
                result = chat.results.pop(0)
                if result is None:
                    return None
                return schema.model_validate(result)

        return Bound()


def requirement_data():
    return {
        "title": "午夜出屏",
        "genre": "奇幻喜剧",
        "target_audience": "年轻上班族",
        "core_idea": "程序员小林在零点看见角色阿沐从屏幕里走出来，两人一起改完最后一版漫画。",
    }


def outline_data():
    return {
        "opening": "零点的办公室里，阿沐从屏幕中跨出来。",
        "conflict": "漫画应用马上发版，阿沐却不肯回到屏幕里。",
        "development": "小林试图用代码把阿沐送回去，反而让办公室变成漫画分格。",
        "turning_point": "阿沐改完最后一镜，主动站回屏幕边缘。",
        "ending": "发版成功，阿沐在屏幕里向小林挥手。",
        "theme": "作品被认真对待之后，角色才肯回家。",
    }


def character_data():
    return {
        "character_id": "char_lin",
        "name": "小林",
        "identity": "漫画应用程序员",
        "personality": "较真",
        "appearance": "短发圆框眼镜",
        "clothing": "皱衬衫",
        "visual_keywords": ["短发", "眼镜"],
    }


def scene_data():
    return {
        "scene_id": "scene_office",
        "name": "深夜办公室",
        "time": "零点",
        "location": "工位与屏幕相对",
        "lighting": "屏幕冷光",
        "colors": "蓝灰",
        "visual_keywords": ["工位", "屏幕"],
    }


def storyboard_data():
    return {
        "shot_id": "shot_one",
        "order": 1,
        "duration_seconds": 9,
        "scene_id": "scene_office",
        "character_ids": ["char_lin"],
        "action": "小林抬头看见阿沐跨出屏幕。",
        "composition": "中景，屏幕在左，小林在右。",
        "dialogue": "",
        "camera_motion": "固定机位",
        "start_frame_prompt": "深夜办公室，小林坐在屏幕前。",
        "end_frame_prompt": "阿沐站在办公桌旁。",
        "video_prompt": "阿沐从屏幕里跨到桌旁。",
    }


@pytest.mark.parametrize(
    ("model_provider", "base_attr", "base_url", "thinking"),
    [
        (
            "openai",
            "openai_api_base",
            "https://api.deepseek.com",
            {"thinking": {"type": "disabled"}},
        ),
        (
            "anthropic",
            "anthropic_api_url",
            "https://api.deepseek.com/anthropic",
            {"type": "disabled"},
        ),
    ],
)
def test_model_provider_selects_deepseek_base_url(
    model_provider, base_attr, base_url, thinking
):
    model = DeepSeekTextModel(
        api_key="test-key",
        model="deepseek-v4-pro",
        model_provider=model_provider,
    )

    assert getattr(model._chat, base_attr) == base_url
    assert model._chat.max_tokens == 8192
    thinking_attr = "extra_body" if model_provider == "openai" else "thinking"
    assert getattr(model._chat, thinking_attr) == thinking


def test_unknown_model_provider_is_rejected():
    with pytest.raises(ValueError, match="openai"):
        DeepSeekTextModel(api_key="k", model="deepseek-v4-pro", model_provider="volc")


def test_analyze_requirement_returns_structured_requirement():
    chat = RecordingStructuredChat([requirement_data()])
    model = DeepSeekTextModel(api_key="k", model="deepseek-flash", chat_model=chat)

    result = model.analyze_requirement("深夜办公室，角色走出屏幕")

    assert isinstance(result, CreativeRequirement)
    assert result.title == "午夜出屏"
    call = chat.calls[0]
    assert call["schema"] is CreativeRequirement
    assert call["kwargs"]["method"] == "function_calling"
    assert call["messages"] == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "深夜办公室，角色走出屏幕"},
    ]


def test_generate_story_outline_sends_requirement_payload():
    chat = RecordingStructuredChat([outline_data()])
    model = DeepSeekTextModel(api_key="k", model="deepseek-flash", chat_model=chat)
    requirement = CreativeRequirement.model_validate(requirement_data())

    result = model.generate_story_outline(requirement)

    assert isinstance(result, StoryOutline)
    call = chat.calls[0]
    assert call["schema"] is StoryOutline
    assert call["messages"][0] == {"role": "system", "content": STORY_PROMPT}
    assert json.loads(call["messages"][1]["content"]) == {
        "requirement": requirement.model_dump(mode="json")
    }


def test_generate_characters_and_scenes_unwrap_lists():
    chat = RecordingStructuredChat(
        [{"characters": [character_data()]}, {"scenes": [scene_data()]}]
    )
    model = DeepSeekTextModel(api_key="k", model="deepseek-flash", chat_model=chat)
    requirement = CreativeRequirement.model_validate(requirement_data())
    outline = StoryOutline.model_validate(outline_data())

    characters = model.generate_characters(requirement, outline)
    scenes = model.generate_scenes(requirement, outline)

    assert characters == [CharacterProfile.model_validate(character_data())]
    assert scenes == [SceneProfile.model_validate(scene_data())]
    assert chat.calls[0]["messages"][0]["content"] == CHARACTER_PROMPT
    assert chat.calls[1]["messages"][0]["content"] == SCENE_PROMPT


def test_generate_storyboard_puts_closed_ids_first():
    chat = RecordingStructuredChat([{"storyboard_list": [storyboard_data()]}])
    model = DeepSeekTextModel(api_key="k", model="deepseek-flash", chat_model=chat)
    requirement = CreativeRequirement.model_validate(requirement_data())
    outline = StoryOutline.model_validate(outline_data())
    characters = [CharacterProfile.model_validate(character_data())]
    scenes = [SceneProfile.model_validate(scene_data())]

    result = model.generate_storyboard(requirement, outline, characters, scenes)

    assert result == [Storyboard.model_validate(storyboard_data())]
    payload = json.loads(chat.calls[0]["messages"][1]["content"])
    assert chat.calls[0]["messages"][0]["content"] == STORYBOARD_PROMPT
    assert payload["target_shot_count"] == requirement.shot_count
    assert payload["target_duration_seconds"] == requirement.duration_seconds
    assert payload["allowed_character_ids"] == ["char_lin"]
    assert payload["allowed_scene_ids"] == ["scene_office"]


def test_missing_structured_result_raises():
    chat = RecordingStructuredChat([None])
    model = DeepSeekTextModel(api_key="k", model="deepseek-flash", chat_model=chat)

    with pytest.raises(ValueError, match="没有返回可解析的结构化需求"):
        model.analyze_requirement("一段创意")


def test_build_text_model_selects_deepseek(monkeypatch):
    monkeypatch.setattr(text_model_settings, "provider", "deepseek")
    monkeypatch.setattr(deepseek_settings, "api_key", "test-key")
    monkeypatch.setattr(deepseek_settings, "model", "deepseek-v4-pro")
    monkeypatch.setattr(deepseek_settings, "model_provider", "openai")

    model = build_text_model()

    assert isinstance(model, DeepSeekTextModel)
    assert model._chat.openai_api_base == "https://api.deepseek.com"


def test_build_text_model_requires_deepseek_settings(monkeypatch):
    monkeypatch.setattr(text_model_settings, "provider", "deepseek")
    monkeypatch.setattr(deepseek_settings, "api_key", " ")
    monkeypatch.setattr(deepseek_settings, "model", "deepseek-v4-pro")
    monkeypatch.setattr(deepseek_settings, "model_provider", "anthropic")

    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
        build_text_model()


def test_build_text_model_requires_model_provider(monkeypatch):
    monkeypatch.setattr(text_model_settings, "provider", "deepseek")
    monkeypatch.setattr(deepseek_settings, "api_key", "test-key")
    monkeypatch.setattr(deepseek_settings, "model", "deepseek-v4-pro")
    monkeypatch.setattr(deepseek_settings, "model_provider", " ")

    with pytest.raises(RuntimeError, match="DEEPSEEK_MODEL_PROVIDER"):
        build_text_model()
