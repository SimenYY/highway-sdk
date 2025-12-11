from pydantic_settings import BaseSettings


class MQTTConfig(BaseSettings):
    BROKER_HOST: str = "localhost"
    BROKER_PORT: int = 1883
    BROKER_PWD: str = ""
    BROKER_USR: str = ""


mqtt_settings = MQTTConfig()
