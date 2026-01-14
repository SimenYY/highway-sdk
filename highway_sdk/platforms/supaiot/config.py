from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["SupaiotConfig"]


class SupaiotConfig(BaseSettings):
    """物联智控配置"""

    model_config = SettingsConfigDict(env_prefix="SUPAIOT_", env_file=[".env.local", ".env"], extra="allow")

    API_BASE_URL: str = ""  # 物联智控服务地址，例如http://192.168.1.1:8080
    API_APP_ID: str = ""  # 物联智控APP_ID
    API_APP_SECRET: str = ""  # 物联智控APP_SECRET
    API_PROJECT_ID: str = ""  # 物联智控项目ID

    # MQTT服务
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 9312
    MQTT_BROKER_USR: str = "mviotroot"
    MQTT_BROKER_PWD: str = "mviotroot123"
    MQTT_QOS: int = 0
