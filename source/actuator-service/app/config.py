from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "actuator-group"
    simulator_base_url: str = "http://localhost:8080"
    service_port: int = 8004

    class Config:
        env_file = ".env"


settings = Settings()
