from server.config.deepseek_settings import deepseek_settings
from server.config.fake_settings import fake_settings
from server.config.text_model_settings import text_model_settings

from .deepseek_text_model import DeepSeekTextModel
from .fack_text_model import FakeTextModel
from .text_model import TextModel


def build_text_model() -> TextModel:
    provider = text_model_settings.provider.strip().lower() or "fake"
    if provider == "fake":
        planning_fault = fake_settings.planning_fault.strip().lower() or "none"
        if planning_fault not in {"none", "characters", "scenes"}:
            raise ValueError(f"不支持的 FAKE_PLANNING_FAULT：{planning_fault}")
        storyboard_fault = fake_settings.storyboard_fault.strip().lower() or "none"
        if storyboard_fault not in {"none", "duplicate_id", "unknown_character", "duration_mismatch"}:
            raise ValueError(f"不支持的 FAKE_STORYBOARD_FAULT：{storyboard_fault}")
        return FakeTextModel(planning_fault=planning_fault, storyboard_fault=storyboard_fault)
    if provider == "deepseek":
        api_key = deepseek_settings.api_key.strip()
        model = deepseek_settings.model.strip()
        model_provider = deepseek_settings.model_provider.strip().lower()
        if not api_key or not model or not model_provider:
            raise RuntimeError(
                "使用 deepseek 时必须配置 DEEPSEEK_API_KEY、DEEPSEEK_MODEL 和 DEEPSEEK_MODEL_PROVIDER"
            )
        return DeepSeekTextModel(
            api_key=api_key,
            model=model,
            model_provider=model_provider,
        )
    raise ValueError(f"不支持的 TEXT_MODEL_PROVIDER：{provider}")
