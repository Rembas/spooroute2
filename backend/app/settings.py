from pydantic import BaseModel
import os

class Settings(BaseModel):
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    demo_mode: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    gtfs_sqlite_path: str = os.getenv("GTFS_SQLITE_PATH", "/data/gtfs.sqlite")

settings = Settings()