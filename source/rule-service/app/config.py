from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "mars_iot"
    service_port: int = 8003

    class Config:
        env_file = ".env"


settings = Settings()
