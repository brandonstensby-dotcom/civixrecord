"""
CivixRecord Backend Configuration & Settings
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CivixRecord-OS Civic Intelligence Platform"
    VERSION: str = "0.4.1"
    API_V1_STR: str = "/api/v1"
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Audio capture & buffer limits
    SAMPLE_RATE: int = 16000
    AUDIO_CHUNK_MS: int = 250
    CUSUM_THRESHOLD: float = 0.85
    CUSUM_DRIFT: float = 0.05
    
    # Statutory & Parliamentary Defaults
    DEFAULT_QUORUM_PERCENT: float = 0.50
    MANDATORY_IN_CAMERA_FENCE: bool = True
    
    # Micro-VM IPC Socket
    KERNEL_SOCKET: str = "127.0.0.1:9443"
    
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    model_config = SettingsConfigDict(env_prefix="CIVIX_", case_sensitive=True)


settings = Settings()
