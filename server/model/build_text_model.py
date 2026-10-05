from server.config.ark_settings import ark_settings
from server.config.fake_settings import fake_settings
from server.config.text_model_settings import text_model_settings

from .ark_text_model import ArkTextModel
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
    if provider == "ark":
        api_key = ark_settings.api_key.strip()
        model = ark_settings.model.strip()
        if not api_key or not model:
            raise RuntimeError("使用 ark 时必须配置 ARK_API_KEY 和 ARK_MODEL")
        return ArkTextModel(api_key=api_key, model=model)
    raise ValueError(f"不支持的 TEXT_MODEL_PROVIDER：{provider}")
