"""
Database utilities - Shared DB configuration for all stores.

Provides single source of truth for database path.
"""

import os
from pathlib import Path

# Default database path
_DEFAULT_DB_PATH = os.path.join("database", "socialops.db")


def get_db_path() -> str:
    """
    Get the database file path.
    
    Returns single source of truth for all stores (InboxStore, CRMStore, RepliesStore).
    
    Returns:
        Absolute path to SQLite database file
    """
    # Allow override via environment variable
    db_path = os.getenv("SOCIALOPS_DB_PATH", _DEFAULT_DB_PATH)
    
    # Ensure parent directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    return db_path
