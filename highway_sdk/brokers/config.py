from pydantic_settings import BaseSettings, SettingsConfigDict


class MQTTConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MQTT_", env_file=[".env.local", ".env"], extra="allow")

    BROKER_HOST: str = "localhost"
    BROKER_PORT: int = 1883
    BROKER_PWD: str = ""
    BROKER_USR: str = ""
