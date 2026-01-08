"""
Search Service - Unified search across threads, leads, and replies.

Provides LIKE-based search on sqlite tables.
"""

import sqlite3
import logging
from typing import List, Dict, Optional
from services.db import get_db_path

logger = logging.getLogger(__name__)


def search_threads(query: str, limit: int = 50) -> List[Dict]:
    """
    Search threads by title or message text.
    
    Args:
        query: Search query string
        limit: Max results to return
    
    Returns:
        List of dicts with: id, title, platform, preview, route_target, type
    """
    if not query or not query.strip():
        return []
    
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        
        # Search in threads table (title) and messages table (text)
        cursor.execute("""
            SELECT DISTINCT t.thread_id, t.title, t.platform, t.updated_at as last_message_at
            FROM threads t
            LEFT JOIN messages m ON t.thread_id = m.thread_id
            WHERE t.title LIKE ? OR m.text LIKE ?
            ORDER BY t.updated_at DESC
            LIMIT ?
        """, (search_term, search_term, limit))
        
        results = []
        for row in cursor.fetchall():
            # Get preview from latest message
            cursor.execute("""
                SELECT text FROM messages 
                WHERE thread_id = ? 
                ORDER BY timestamp DESC LIMIT 1
            """, (row['thread_id'],))
            msg_row = cursor.fetchone()
            preview = msg_row['text'][:100] + "..." if msg_row else "No messages"
            
            results.append({
                'id': row['thread_id'],
                'title': row['title'],
                'platform': row['platform'],
                'preview': preview,
                'route_target': 'inbox',
                'type': 'thread'
            })
        
        conn.close()
        return results
    
    except Exception as e:
        logger.error(f"Search threads error: {e}", exc_info=True)
        return []


def search_leads(query: str, limit: int = 50) -> List[Dict]:
    """
    Search leads by name, phone, notes, or tags.
    
    Args:
        query: Search query string
        limit: Max results to return
    
    Returns:
        List of dicts with: id, name, status, preview, route_target, type
    """
    if not query or not query.strip():
        return []
    
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        
        cursor.execute("""
            SELECT id, name, status, notes, tags, phone
            FROM leads
            WHERE name LIKE ? OR notes LIKE ? OR tags LIKE ? OR phone LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (search_term, search_term, search_term, search_term, limit))
        
        results = []
        for row in cursor.fetchall():
            preview = row['notes'][:100] if row['notes'] else f"Status: {row['status']}"
            if row['phone']:
                preview = f"Phone: {row['phone']} | {preview}"
            
            results.append({
                'id': row['id'],
                'name': row['name'],
                'status': row['status'],
                'preview': preview,
                'route_target': 'leads',
                'type': 'lead'
            })
        
        conn.close()
        return results
    
    except Exception as e:
        logger.error(f"Search leads error: {e}", exc_info=True)
        return []


def search_replies(query: str, limit: int = 50) -> List[Dict]:
    """
    Search saved replies by title, body, or tags.
    
    Args:
        query: Search query string
        limit: Max results to return
    
    Returns:
        List of dicts with: id, title, preview, route_target, type
    """
    if not query or not query.strip():
        return []
    
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        
        cursor.execute("""
            SELECT id, title, body, tags, lang
            FROM replies
            WHERE title LIKE ? OR body LIKE ? OR tags LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (search_term, search_term, search_term, limit))
        
        results = []
        for row in cursor.fetchall():
            preview = row['body'][:100] + "..." if len(row['body']) > 100 else row['body']
            
            results.append({
                'id': row['id'],
                'title': row['title'],
                'preview': preview,
                'lang': row['lang'],
                'route_target': 'replies',
                'type': 'reply'
            })
        
        conn.close()
        return results
    
    except Exception as e:
        logger.error(f"Search replies error: {e}", exc_info=True)
        return []


def search_all(query: str, limit: int = 50) -> List[Dict]:
    """
    Search across all entities (threads, leads, replies).
    
    Args:
        query: Search query string
        limit: Max results per type
    
    Returns:
        Combined list of results sorted by relevance
    """
    threads = search_threads(query, limit)
    leads = search_leads(query, limit)
    replies = search_replies(query, limit)
    
    # Combine and return (already sorted by recency within each type)
    return threads + leads + replies
