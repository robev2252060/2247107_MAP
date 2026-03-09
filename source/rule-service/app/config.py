from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://mars:mars_secure_pass@localhost:5432/mars_iot"
    service_port: int = 8003

    class Config:
        env_file = ".env"


settings = Settings()
