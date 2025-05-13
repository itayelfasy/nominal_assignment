"""Application configuration settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # QuickBooks OAuth settings
    QUICKBOOKS_CLIENT_ID: str
    QUICKBOOKS_CLIENT_SECRET: str
    QUICKBOOKS_REDIRECT_URI: str
    QUICKBOOKS_SANDBOX_URL: str
    QUICKBOOKS_AUTH_URL: str
    QUICKBOOKS_TOKEN_URL: str
    QUICKBOOKS_SCOPE: str
    QUICKBOOKS_STATE: str
    QUICKBOOKS_SANDBOX_REALM_ID: str
    
    # Database settings
    DATABASE_URL: str

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings.
    
    Returns:
        Settings: Application settings instance.
    """
    return Settings() 