from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    simulator_base_url: str = "http://localhost:8080"
    kafka_bootstrap_servers: str = "localhost:9092"
    poll_interval_seconds: int = 5
    service_port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
