import os
from functools import lru_cache
import chromadb
from chromadb.config import Settings

from app.core.config import settings

@lru_cache(maxsize=1)
def get_chroma_client():
    """Get a singleton instance of Chroma client with consistent settings"""
    # Ensure the persist directory exists
    os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
    
    # Create consistent settings
    client_settings = Settings(
        persist_directory=settings.VECTOR_DB_PATH,
        anonymized_telemetry=False,
        allow_reset=True,
        is_persistent=True
    )
    
    # Return singleton client instance
    return chromadb.PersistentClient(path=settings.VECTOR_DB_PATH, settings=client_settings) 