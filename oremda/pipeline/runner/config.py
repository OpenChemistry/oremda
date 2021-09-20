from pydantic import BaseSettings


class Settings(BaseSettings):
    SERVER_URL: str = "ws://localhost:8000/api/v1/rpc"
    OREMDA_VAR_DIR: str
    OREMDA_DATA_DIR: str
    OREMDA_DIR: str

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
