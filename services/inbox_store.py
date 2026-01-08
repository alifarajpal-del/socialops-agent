"""
Inbox Store - DB-backed unified inbox storage for SocialOps Agent.

Manages conversation threads and messages across Instagram, Facebook, WhatsApp.
Provides JSON import for testing without real integrations.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from app_config.settings import DATABASE_PATH

logger = logging.getLogger(__name__)


class InboxStore:
    """
    DB-backed storage for unified inbox.
    
    Tables:
    - threads: Conversation threads with metadata
    - messages: Individual messages linked to threads
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize inbox store.
        
        Args:
            db_path: Path to SQLite database file (uses config default if None)
        """
        self.db_path = db_path or DATABASE_PATH
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
        logger.info(f"InboxStore initialized with DB: {self.db_path}")
    
    def init_db(self) -> None:
        """Initialize database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Threads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                thread_id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                title TEXT,
                updated_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                sender_id TEXT NOT NULL,
                sender_name TEXT,
                text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                raw_json TEXT,
                FOREIGN KEY (thread_id) REFERENCES threads(thread_id)
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_threads_platform_updated 
            ON threads(platform, updated_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_thread_timestamp 
            ON messages(thread_id, timestamp)
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def upsert_thread(
        self,
        thread_id: str,
        platform: str,
        updated_at: str,
        title: Optional[str] = None
    ) -> None:
        """
        Insert or update thread.
        
        Args:
            thread_id: Unique thread identifier
            platform: Platform name (instagram, facebook, whatsapp)
            updated_at: ISO format timestamp of last update
            title: Thread title (derived from messages if None)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO threads (thread_id, platform, title, updated_at, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(thread_id) DO UPDATE SET
                updated_at=excluded.updated_at,
                title=COALESCE(excluded.title, title)
        """, (thread_id, platform.lower(), title, updated_at, updated_at))
        
        conn.commit()
        conn.close()
        logger.debug(f"Upserted thread: {thread_id}")
    
    def add_message(
        self,
        thread_id: str,
        platform: str,
        sender_id: str,
        sender_name: str,
        text: str,
        timestamp: str,
        raw_json: Optional[str] = None
    ) -> None:
        """
        Add message to thread.
        
        Args:
            thread_id: Thread identifier
            platform: Platform name
            sender_id: Sender's platform user ID
            sender_name: Sender's display name
            text: Message text
            timestamp: ISO format timestamp
            raw_json: Raw message JSON for reference
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages 
            (thread_id, platform, sender_id, sender_name, text, timestamp, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (thread_id, platform.lower(), sender_id, sender_name, text, timestamp, raw_json))
        
        conn.commit()
        conn.close()
        logger.debug(f"Added message to thread: {thread_id}")
    
    def list_threads(self, platform_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List threads, optionally filtered by platform.
        
        Args:
            platform_filter: Filter by platform (None for all)
            
        Returns:
            List of thread dictionaries sorted by updated_at DESC
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if platform_filter:
            cursor.execute("""
                SELECT thread_id, platform, title, updated_at, created_at
                FROM threads
                WHERE platform = ?
                ORDER BY updated_at DESC
            """, (platform_filter.lower(),))
        else:
            cursor.execute("""
                SELECT thread_id, platform, title, updated_at, created_at
                FROM threads
                ORDER BY updated_at DESC
            """)
        
        threads = []
        for row in cursor.fetchall():
            threads.append({
                'thread_id': row[0],
                'platform': row[1],
                'title': row[2],
                'updated_at': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        return threads
    
    def get_thread_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Get messages for a thread.
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            List of message dictionaries sorted by timestamp ASC
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT message_id, thread_id, platform, sender_id, sender_name, 
                   text, timestamp, raw_json
            FROM messages
            WHERE thread_id = ?
            ORDER BY timestamp ASC
        """, (thread_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'message_id': row[0],
                'thread_id': row[1],
                'platform': row[2],
                'sender_id': row[3],
                'sender_name': row[4],
                'text': row[5],
                'timestamp': row[6],
                'raw_json': row[7]
            })
        
        conn.close()
        return messages
    
    def import_from_json(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Import messages from JSON format for testing.
        
        Expected format:
        [
            {
                "platform": "instagram|facebook|whatsapp",
                "thread_id": "unique_id" (optional, auto-generated if missing),
                "sender_id": "user_id",
                "sender_name": "Display Name",
                "text": "Message text",
                "timestamp": "2026-01-08T10:00:00Z" (optional, uses now if missing)
            },
            ...
        ]
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            {
                "imported": count,
                "threads_created": count,
                "errors": [error_messages]
            }
        """
        imported = 0
        threads_created = set()
        errors = []
        
        for idx, msg in enumerate(messages):
            try:
                # Validate required fields
                if 'platform' not in msg or 'sender_name' not in msg or 'text' not in msg:
                    errors.append(f"Message {idx}: Missing required fields")
                    continue
                
                platform = msg['platform'].lower()
                if platform not in ['instagram', 'facebook', 'whatsapp']:
                    errors.append(f"Message {idx}: Invalid platform '{platform}'")
                    continue
                
                # Generate thread_id if missing
                thread_id = msg.get('thread_id') or f"{platform}_{msg.get('sender_id', msg['sender_name'].replace(' ', '_'))}"
                
                # Use current timestamp if missing
                timestamp = msg.get('timestamp') or datetime.now().isoformat()
                
                # Ensure thread exists
                if thread_id not in threads_created:
                    self.upsert_thread(
                        thread_id=thread_id,
                        platform=platform,
                        updated_at=timestamp,
                        title=msg['sender_name']
                    )
                    threads_created.add(thread_id)
                
                # Add message
                self.add_message(
                    thread_id=thread_id,
                    platform=platform,
                    sender_id=msg.get('sender_id', thread_id),
                    sender_name=msg['sender_name'],
                    text=msg['text'],
                    timestamp=timestamp,
                    raw_json=json.dumps(msg)
                )
                
                imported += 1
                
            except Exception as e:
                errors.append(f"Message {idx}: {str(e)}")
                logger.error(f"Import error for message {idx}: {e}")
        
        logger.info(f"Imported {imported} messages into {len(threads_created)} threads")
        
        return {
            'imported': imported,
            'threads_created': len(threads_created),
            'errors': errors
        }


# Global singleton
_inbox_store = None


def get_inbox_store() -> InboxStore:
    """Get or create global inbox store instance."""
    global _inbox_store
    if _inbox_store is None:
        _inbox_store = InboxStore()
    return _inbox_store
