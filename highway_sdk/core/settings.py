from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = [
    "JsonSettings",
    "YamlSettings",
]


class YamlSettings(BaseSettings):
    """Yaml 配置源基类。

    子类可通过 ``model_config`` 自定义 ``yaml_file``、``yaml_file_encoding``、``env_prefix`` 等选项，
    并按需重写 ``settings_customise_sources`` 注入 ``YamlConfigSettingsSource``。
    """

    model_config = SettingsConfigDict(yaml_file="config.yaml", yaml_file_encoding="utf-8", env_prefix="hw_")


class JsonSettings(BaseSettings):
    """Json 配置源基类。

    子类可通过 ``model_config`` 自定义 ``json_file``、``json_file_encoding``、``env_prefix`` 等选项，
    并按需重写 ``settings_customise_sources`` 注入 ``JsonConfigSettingsSource``。
    """

    model_config = SettingsConfigDict(json_file="config.json", json_file_encoding="utf-8", env_prefix="hw_")
