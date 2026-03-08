from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "state-group"
    service_port: int = 8002

    class Config:
        env_file = ".env"


settings = Settings()
