from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration, read from environment variables or the `.env` file."""

    # extra="ignore": `.env` may hold variables for later PRs.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    # Optional. Without it, no traces are sent to Logfire.
    logfire_token: str | None = None
    # How long the placeholder waits before each status change. Tests set it to 0.
    placeholder_step_seconds: float = 2.0
