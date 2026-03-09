from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "processing-group"
    database_url: str = "postgresql://mars:mars_secure_pass@localhost:5432/mars_iot"
    service_port: int = 8001

    class Config:
        env_file = ".env"


settings = Settings()
