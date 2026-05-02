from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "External Movie Cache API"
    database_url: str = "sqlite:///./app.db"

    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_api_key: str = ""
    cache_ttl_seconds: int = 3600
    http_timeout_seconds: int = 10

    model_config = ConfigDict(env_file=".env")


settings = Settings()
