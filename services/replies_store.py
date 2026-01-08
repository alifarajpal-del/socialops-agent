"""
Replies Store - Saved reply templates for SocialOps Agent.

Manages a library of reusable reply templates.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from app_config.settings import DATABASE_PATH

logger = logging.getLogger(__name__)


class RepliesStore:
    """
    DB-backed storage for saved reply templates.
    
    Table:
    - replies: Saved reply templates with scope, language, tags
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize Replies store.
        
        Args:
            db_path: Path to SQLite database file (uses config default if None)
        """
        self.db_path = db_path or DATABASE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
        logger.info(f"RepliesStore initialized with DB: {self.db_path}")
    
    def init_db(self) -> None:
        """Initialize replies table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                scope TEXT DEFAULT 'core',
                plugin_name TEXT,
                lang TEXT DEFAULT 'en',
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                tags TEXT
            )
        """)
        
        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_replies_scope_lang 
            ON replies(scope, lang)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_replies_plugin 
            ON replies(plugin_name)
        """)
        
        conn.commit()
        conn.close()
        logger.info("Replies table initialized")
    
    def create_reply(
        self,
        title: str,
        body: str,
        lang: str = "en",
        scope: str = "core",
        plugin_name: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """
        Create a new reply template.
        
        Args:
            title: Reply title/name
            body: Reply text content
            lang: Language code (en, ar, fr)
            scope: core or plugin
            plugin_name: Plugin name if scope=plugin
            tags: List of tags for filtering
            
        Returns:
            Reply ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        tags_json = json.dumps(tags) if tags else None
        
        cursor.execute("""
            INSERT INTO replies (created_at, updated_at, scope, plugin_name, lang, title, body, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (now, now, scope, plugin_name, lang, title, body, tags_json))
        
        reply_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Created reply #{reply_id}: {title}")
        return reply_id
    
    def list_replies(
        self,
        scope: Optional[str] = None,
        plugin: Optional[str] = None,
        lang: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List reply templates with optional filters.
        
        Args:
            scope: Filter by scope (core, plugin, or None for all)
            plugin: Filter by plugin name
            lang: Filter by language
            
        Returns:
            List of reply dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM replies WHERE 1=1"
        params = []
        
        if scope:
            query += " AND scope = ?"
            params.append(scope)
        
        if plugin:
            query += " AND plugin_name = ?"
            params.append(plugin)
        
        if lang:
            query += " AND lang = ?"
            params.append(lang)
        
        query += " ORDER BY updated_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        replies = []
        for row in rows:
            reply = dict(row)
            # Parse tags JSON
            if reply['tags']:
                try:
                    reply['tags'] = json.loads(reply['tags'])
                except:
                    reply['tags'] = []
            else:
                reply['tags'] = []
            replies.append(reply)
        
        return replies
    
    def get_reply(self, reply_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a single reply by ID.
        
        Args:
            reply_id: Reply ID
            
        Returns:
            Reply dictionary or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM replies WHERE id = ?", (reply_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        reply = dict(row)
        if reply['tags']:
            try:
                reply['tags'] = json.loads(reply['tags'])
            except:
                reply['tags'] = []
        else:
            reply['tags'] = []
        
        return reply
    
    def update_reply(
        self,
        reply_id: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """
        Update a reply template.
        
        Args:
            reply_id: Reply ID
            title: New title (optional)
            body: New body (optional)
            tags: New tags list (optional)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current reply
        cursor.execute("SELECT * FROM replies WHERE id = ?", (reply_id,))
        current = cursor.fetchone()
        if not current:
            conn.close()
            logger.warning(f"Reply {reply_id} not found")
            return
        
        now = datetime.utcnow().isoformat()
        
        if title is not None:
            cursor.execute("UPDATE replies SET title = ?, updated_at = ? WHERE id = ?", 
                         (title, now, reply_id))
        
        if body is not None:
            cursor.execute("UPDATE replies SET body = ?, updated_at = ? WHERE id = ?", 
                         (body, now, reply_id))
        
        if tags is not None:
            tags_json = json.dumps(tags)
            cursor.execute("UPDATE replies SET tags = ?, updated_at = ? WHERE id = ?", 
                         (tags_json, now, reply_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated reply #{reply_id}")
    
    def delete_reply(self, reply_id: int) -> None:
        """
        Delete a reply template.
        
        Args:
            reply_id: Reply ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM replies WHERE id = ?", (reply_id,))
        
        conn.commit()
        conn.close()
        logger.info(f"Deleted reply #{reply_id}")
    
    def seed_defaults(self) -> int:
        """
        Seed default reply templates if table is empty.
        
        Returns:
            Number of replies created
        """
        # Check if table is empty
        if len(self.list_replies()) > 0:
            logger.info("Replies table not empty, skipping seed")
            return 0
        
        # Default replies (10 total: 5 English + 5 Arabic)
        defaults = [
            # English
            {
                "lang": "en",
                "title": "Welcome Message",
                "body": "Hi! Thank you for reaching out. How can I help you today?",
                "tags": ["greeting", "welcome"]
            },
            {
                "lang": "en",
                "title": "Appointment Confirmation",
                "body": "Your appointment has been confirmed for {date} at {time}. Looking forward to seeing you!",
                "tags": ["appointment", "confirmation"]
            },
            {
                "lang": "en",
                "title": "Price Inquiry Response",
                "body": "Thank you for your interest! Our prices start at {price}. Would you like to schedule a consultation?",
                "tags": ["pricing", "inquiry"]
            },
            {
                "lang": "en",
                "title": "Follow-up Reminder",
                "body": "Hi! Just checking in to see if you have any questions or would like to schedule your next appointment.",
                "tags": ["follow-up", "reminder"]
            },
            {
                "lang": "en",
                "title": "Thank You",
                "body": "Thank you for choosing us! We appreciate your business and look forward to serving you again.",
                "tags": ["thanks", "appreciation"]
            },
            # Arabic
            {
                "lang": "ar",
                "title": "رسالة ترحيب",
                "body": "مرحباً! شكراً لتواصلك معنا. كيف يمكنني مساعدتك اليوم؟",
                "tags": ["ترحيب", "تحية"]
            },
            {
                "lang": "ar",
                "title": "تأكيد الموعد",
                "body": "تم تأكيد موعدك ليوم {date} في تمام الساعة {time}. نتطلع لرؤيتك!",
                "tags": ["موعد", "تأكيد"]
            },
            {
                "lang": "ar",
                "title": "الرد على استفسار السعر",
                "body": "شكراً لاهتمامك! أسعارنا تبدأ من {price}. هل ترغب في حجز استشارة؟",
                "tags": ["أسعار", "استفسار"]
            },
            {
                "lang": "ar",
                "title": "تذكير المتابعة",
                "body": "مرحباً! أردت فقط التأكد من عدم وجود أي أسئلة أو إذا كنت ترغب في حجز موعدك القادم.",
                "tags": ["متابعة", "تذكير"]
            },
            {
                "lang": "ar",
                "title": "شكراً لك",
                "body": "شكراً لاختيارك لنا! نقدر عملك ونتطلع لخدمتك مرة أخرى.",
                "tags": ["شكر", "تقدير"]
            },
        ]
        
        count = 0
        for default in defaults:
            self.create_reply(
                title=default["title"],
                body=default["body"],
                lang=default["lang"],
                scope="core",
                tags=default.get("tags", [])
            )
            count += 1
        
        logger.info(f"Seeded {count} default replies")
        return count
