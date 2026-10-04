from server.config.ark_settings import ark_settings
from server.config.text_model_settings import text_model_settings

from .ark_text_model import ArkTextModel
from .fack_text_model import FakeTextModel
from .text_model import TextModel


def build_text_model() -> TextModel:
    provider = text_model_settings.provider.strip().lower() or "fake"
    if provider == "fake":
        return FakeTextModel()
    if provider == "ark":
        api_key = ark_settings.api_key.strip()
        model = ark_settings.model.strip()
        if not api_key or not model:
            raise RuntimeError("使用 ark 时必须配置 ARK_API_KEY 和 ARK_MODEL")
        return ArkTextModel(api_key=api_key, model=model)
    raise ValueError(f"不支持的 TEXT_MODEL_PROVIDER：{provider}")
