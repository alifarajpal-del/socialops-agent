"""
CRM Store - Leads and Tasks management for SocialOps Agent.

Manages leads pipeline and follow-up tasks.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from services.db import get_db_path

logger = logging.getLogger(__name__)


class CRMStore:
    """
    DB-backed storage for CRM (leads and tasks).
    
    Tables:
    - leads: Lead/contact records with status pipeline
    - tasks: Follow-up tasks linked to leads/threads
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize CRM store.
        
        Args:
            db_path: Path to SQLite database file (uses shared default if None)
        """
        self.db_path = db_path or get_db_path()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
        logger.info(f"CRMStore initialized with DB: {self.db_path}")
    
    def init_db(self) -> None:
        """Initialize CRM tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Leads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                source_platform TEXT,
                thread_id TEXT,
                name TEXT,
                phone TEXT,
                city TEXT,
                status TEXT DEFAULT 'new',
                tags TEXT,
                notes TEXT
            )
        """)
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                due_at TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                type TEXT DEFAULT 'followup',
                related_lead_id INTEGER,
                related_thread_id TEXT,
                title TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (related_lead_id) REFERENCES leads(id)
            )
        """)
        
        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_leads_status 
            ON leads(status, updated_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_leads_thread 
            ON leads(thread_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_due 
            ON tasks(completed, due_at)
        """)
        
        conn.commit()
        conn.close()
        logger.info("CRM tables initialized")
    
    def create_lead_from_thread(
        self, 
        thread_id: str, 
        platform: str, 
        name: Optional[str] = None
    ) -> int:
        """
        Create a lead from a thread.
        
        Args:
            thread_id: Thread ID from inbox
            platform: Source platform (instagram, whatsapp, etc.)
            name: Lead name (optional)
            
        Returns:
            Lead ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if lead already exists for this thread
        cursor.execute(
            "SELECT id FROM leads WHERE thread_id = ?",
            (thread_id,)
        )
        existing = cursor.fetchone()
        if existing:
            conn.close()
            logger.info(f"Lead already exists for thread {thread_id}: {existing[0]}")
            return existing[0]
        
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO leads (created_at, updated_at, source_platform, thread_id, name, status)
            VALUES (?, ?, ?, ?, ?, 'new')
        """, (now, now, platform, thread_id, name))
        
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Created lead {lead_id} from thread {thread_id}")
        return lead_id
    
    def update_lead_status(self, lead_id: int, status: str) -> None:
        """
        Update lead status.
        
        Args:
            lead_id: Lead ID
            status: New status (new, qualified, followup, won, lost)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            UPDATE leads 
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (status, now, lead_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated lead {lead_id} status to {status}")
    
    def add_lead_note(self, lead_id: int, note: str) -> None:
        """
        Add a note to a lead.
        
        Args:
            lead_id: Lead ID
            note: Note text to append
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing notes
        cursor.execute("SELECT notes FROM leads WHERE id = ?", (lead_id,))
        row = cursor.fetchone()
        existing_notes = row[0] if row and row[0] else ""
        
        # Append new note with timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        new_note = f"[{timestamp}] {note}"
        updated_notes = f"{existing_notes}\n{new_note}".strip()
        
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            UPDATE leads 
            SET notes = ?, updated_at = ?
            WHERE id = ?
        """, (updated_notes, now, lead_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Added note to lead {lead_id}")
    
    def set_lead_tags(self, lead_id: int, tags: List[str]) -> None:
        """
        Set lead tags.
        
        Args:
            lead_id: Lead ID
            tags: List of tag strings
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_json = json.dumps(tags)
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            UPDATE leads 
            SET tags = ?, updated_at = ?
            WHERE id = ?
        """, (tags_json, now, lead_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Set tags for lead {lead_id}: {tags}")
    
    def list_leads(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List leads, optionally filtered by status.
        
        Args:
            status: Filter by status (None = all)
            
        Returns:
            List of lead dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT * FROM leads 
                WHERE status = ?
                ORDER BY updated_at DESC
            """, (status,))
        else:
            cursor.execute("""
                SELECT * FROM leads 
                ORDER BY updated_at DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        leads = []
        for row in rows:
            lead = dict(row)
            # Parse tags JSON
            if lead['tags']:
                try:
                    lead['tags'] = json.loads(lead['tags'])
                except:
                    lead['tags'] = []
            else:
                lead['tags'] = []
            leads.append(lead)
        
        return leads
    
    def get_lead(self, lead_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a single lead by ID.
        
        Args:
            lead_id: Lead ID
            
        Returns:
            Lead dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        lead = dict(row)
        # Parse tags JSON
        if lead['tags']:
            try:
                lead['tags'] = json.loads(lead['tags'])
            except:
                lead['tags'] = []
        else:
            lead['tags'] = []
        
        return lead
    
    def get_lead_by_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Get lead associated with a thread.
        
        Args:
            thread_id: Thread ID
            
        Returns:
            Lead dictionary or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM leads WHERE thread_id = ?", (thread_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        lead = dict(row)
        if lead['tags']:
            try:
                lead['tags'] = json.loads(lead['tags'])
            except:
                lead['tags'] = []
        else:
            lead['tags'] = []
        
        return lead
    
    def create_task(
        self,
        title: str,
        due_at_iso: str,
        lead_id: Optional[int] = None,
        thread_id: Optional[str] = None,
        task_type: str = "followup",
        notes: Optional[str] = None
    ) -> int:
        """
        Create a task.
        
        Args:
            title: Task title
            due_at_iso: Due date/time in ISO format
            lead_id: Related lead ID (optional)
            thread_id: Related thread ID (optional)
            task_type: Type (followup, call, custom)
            notes: Task notes (optional)
            
        Returns:
            Task ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO tasks (created_at, due_at, type, related_lead_id, related_thread_id, title, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (now, due_at_iso, task_type, lead_id, thread_id, title, notes))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Created task {task_id}: {title}")
        return task_id
    
    def list_tasks(self, include_completed: bool = False) -> List[Dict[str, Any]]:
        """
        List tasks.
        
        Args:
            include_completed: Include completed tasks
            
        Returns:
            List of task dictionaries sorted by due_at
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if include_completed:
            cursor.execute("SELECT * FROM tasks ORDER BY due_at ASC")
        else:
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE completed = 0 
                ORDER BY due_at ASC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def complete_task(self, task_id: int) -> None:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks 
            SET completed = 1
            WHERE id = ?
        """, (task_id,))
        
        conn.commit()
        conn.close()
        logger.info(f"Completed task {task_id}")
