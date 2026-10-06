from server.config.base_settings import BaseSettingsWithEnv


class DeepSeekSettings(BaseSettingsWithEnv):
    api_key: str = ""
    model: str = ""
    model_provider: str = ""

    model_config = {"env_prefix": "DEEPSEEK_"}


deepseek_settings = DeepSeekSettings()
