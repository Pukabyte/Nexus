import os
from pathlib import Path
from dotenv import load_dotenv


VERSION = "0.1.0"
HTTP_PROXY = os.environ.get("HTTP_PROXY", None)
HEADER_AIO = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
    "Cookie": "fencekey=8e5j3p61b3k0a9b0e44c5bbcecafaa5a2",
}


class Settings:
    """Settings class for handling application settings"""

    def __init__(self) -> None:
        self.root_dir = Path.cwd()
        self.data_dir = self.root_dir / "data"
        self.env_file = self.root_dir / ".env"

        if self.env_file.exists():
            load_dotenv(dotenv_path=self.env_file)

    def get(self, key, default=None):
        """Get environment variable"""
        return os.getenv(key, default)

settings = Settings()