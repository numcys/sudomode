"""Configuration settings for the SudoMode server"""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    # Policy file path
    POLICIES_FILE: str = "policies.yaml"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Slack integration
    SLACK_WEBHOOK_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_policies_path(self) -> Path:
        """Get the absolute path to the policies file"""
        # Try relative to server directory first
        server_dir = Path(__file__).parent.parent.parent
        policies_path = server_dir / self.POLICIES_FILE
        if policies_path.exists():
            return policies_path
        # Fallback to current working directory
        return Path(self.POLICIES_FILE)

settings = Settings()

