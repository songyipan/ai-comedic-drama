from server.config.base_settings import BaseSettingsWithEnv


class FakeSettings(BaseSettingsWithEnv):
    planning_fault: str = ""
    storyboard_fault: str = ""

    model_config = {"env_prefix": "FAKE_"}


fake_settings = FakeSettings()
