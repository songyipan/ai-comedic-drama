from server.config.base_settings import BaseSettingsWithEnv


class TextModelSettings(BaseSettingsWithEnv):
    provider: str = ""

    model_config = {"env_prefix": "TEXT_MODEL_"}


text_model_settings = TextModelSettings()
