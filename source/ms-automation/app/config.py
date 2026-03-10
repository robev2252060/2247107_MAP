from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "ms-automation"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "automation-group"
    kafka_measurements_topic: str = "measurements"
    kafka_actuators_topic: str = "actuators.automation"
    database_url: str = "postgresql://mars:mars_secure_pass@localhost:5432/mars_iot"
    service_port: int = 8001

    class Config:
        env_file = ".env"


settings = Settings()
