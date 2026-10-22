from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration, read from environment variables or the `.env` file."""

    # extra="ignore": `.env` may hold variables for later PRs.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
