from server.config.base_settings import BaseSettingsWithEnv


class ArkSettings(BaseSettingsWithEnv):
    api_key: str = ""
    model: str = ""

    model_config = {"env_prefix": "ARK_"}


ark_settings = ArkSettings()
