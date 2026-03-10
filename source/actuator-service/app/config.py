from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "ms-actuators"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "actuator-group"
    kafka_automation_topic: str = "actuators.automation"
    simulator_base_url: str = "http://localhost:8080"
    service_port: int = 8004

    class Config:
        env_file = ".env"


settings = Settings()
