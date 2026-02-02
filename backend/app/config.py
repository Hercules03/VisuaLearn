"""Configuration management for VisuaLearn backend."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Gemini API
    google_api_key: str
    model: str

    # External Services
    drawio_service_url: str

    # Server Configuration
    debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    # Timeouts (seconds)
    planning_timeout: int = 5
    generation_timeout: int = 12
    review_timeout: int = 3
    image_timeout: int = 4

    # Review Settings
    review_max_iterations: int = 3

    # File Management
    temp_dir: str = "./temp"
    temp_file_ttl: int = 3600  # 1 hour in seconds
    cleanup_interval: int = 600  # 10 minutes in seconds
    max_file_size: int = 5242880  # 5MB in bytes

    # Caching
    cache_size_mb: int = 500
    cache_ttl_seconds: int = 3600

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
