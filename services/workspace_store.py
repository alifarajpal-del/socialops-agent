"""
Workspace Store - Business profile for SocialOps Agent.

Stores workspace/business identity and settings.
"""

import sqlite3
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from services.db import get_db_path

logger = logging.getLogger(__name__)


class WorkspaceStore:
    """
    DB-backed storage for workspace profile.
    
    Table:
    - workspace: Single-row profile with business details
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize Workspace store.
        
        Args:
            db_path: Path to SQLite database file (uses shared default if None)
        """
        self.db_path = db_path or get_db_path()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
        logger.info(f"WorkspaceStore initialized with DB: {self.db_path}")
    
    def init_db(self) -> None:
        """Initialize workspace table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workspace (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                business_name TEXT,
                business_type TEXT,
                city TEXT,
                phone TEXT,
                hours TEXT,
                booking_link TEXT,
                location_link TEXT,
                brand_tone TEXT DEFAULT 'friendly',
                lang_default TEXT DEFAULT 'en'
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Workspace table initialized")
    
    def get_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get workspace profile.
        
        Returns:
            Profile dictionary or None if not set
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM workspace WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return dict(row)
    
    def save_profile(self, profile: Dict[str, Any]) -> None:
        """
        Save or update workspace profile.
        
        Args:
            profile: Profile dictionary with keys:
                - business_name, business_type, city, phone
                - hours, booking_link, location_link
                - brand_tone, lang_default
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        # Check if profile exists
        cursor.execute("SELECT id FROM workspace WHERE id = 1")
        exists = cursor.fetchone()
        
        if exists:
            # Update existing
            cursor.execute("""
                UPDATE workspace 
                SET updated_at = ?,
                    business_name = ?,
                    business_type = ?,
                    city = ?,
                    phone = ?,
                    hours = ?,
                    booking_link = ?,
                    location_link = ?,
                    brand_tone = ?,
                    lang_default = ?
                WHERE id = 1
            """, (
                now,
                profile.get('business_name'),
                profile.get('business_type'),
                profile.get('city'),
                profile.get('phone'),
                profile.get('hours'),
                profile.get('booking_link'),
                profile.get('location_link'),
                profile.get('brand_tone', 'friendly'),
                profile.get('lang_default', 'en')
            ))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO workspace (
                    id, created_at, updated_at,
                    business_name, business_type, city, phone,
                    hours, booking_link, location_link,
                    brand_tone, lang_default
                )
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                now, now,
                profile.get('business_name'),
                profile.get('business_type'),
                profile.get('city'),
                profile.get('phone'),
                profile.get('hours'),
                profile.get('booking_link'),
                profile.get('location_link'),
                profile.get('brand_tone', 'friendly'),
                profile.get('lang_default', 'en')
            ))
        
        conn.commit()
        conn.close()
        logger.info("Workspace profile saved")
