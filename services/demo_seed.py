"""
Demo Seed Service - Populate database with sample data for testing.

Provides idempotent demo data seeding for inbox, CRM, and replies.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional

from services.db import get_db_path

logger = logging.getLogger(__name__)


def seed_demo_data(db_path: Optional[str] = None) -> dict:
    """
    Seed database with demo data for pilot testing.
    
    Idempotent: Checks if demo data already exists before inserting.
    
    Args:
        db_path: Optional database path (uses get_db_path() if None)
    
    Returns:
        Dict with counts: {threads, messages, leads, tasks, replies, skipped}
    """
    if db_path is None:
        db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        counts = {
            'threads': 0,
            'messages': 0,
            'leads': 0,
            'tasks': 0,
            'replies': 0,
            'skipped': False
        }
        
        # Check if demo data already exists
        cursor.execute("SELECT COUNT(*) FROM threads WHERE thread_id LIKE 'demo-%'")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            logger.info(f"Demo data already exists ({existing_count} threads), skipping seed")
            counts['skipped'] = True
            conn.close()
            return counts
        
        # Seed threads
        now = datetime.utcnow().isoformat()
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        two_days_ago = (datetime.utcnow() - timedelta(days=2)).isoformat()
        
        threads = [
            ('demo-thread-1', 'instagram', 'Beauty Appointment Request', yesterday, yesterday),
            ('demo-thread-2', 'whatsapp', 'Product Inquiry', now, now),
            ('demo-thread-3', 'facebook', 'Customer Complaint', two_days_ago, two_days_ago)
        ]
        
        for thread_id, platform, title, created, updated in threads:
            cursor.execute("""
                INSERT INTO threads (thread_id, platform, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (thread_id, platform, title, created, updated))
            counts['threads'] += 1
        
        # Seed messages
        messages = [
            ('demo-thread-1', 'instagram', 'user123', 'Lina', 'Hi! I want to book a hair appointment for Saturday. Available?', yesterday),
            ('demo-thread-1', 'instagram', 'bot', 'Bot', 'Thank you for your message! We will get back to you soon.', yesterday),
            ('demo-thread-1', 'instagram', 'user123', 'Lina', 'Also, do you do bridal makeup?', yesterday),
            
            ('demo-thread-2', 'whatsapp', 'user456', 'Ahmed', 'What is the price for facial treatment?', now),
            ('demo-thread-2', 'whatsapp', 'bot', 'Bot', 'Our facial treatments start at 150 AED. Would you like to book?', now),
            ('demo-thread-2', 'whatsapp', 'user456', 'Ahmed', 'Yes please! When is the earliest?', now),
            
            ('demo-thread-3', 'facebook', 'user789', 'Sara', 'I came yesterday and the service was terrible. Very disappointed.', two_days_ago),
            ('demo-thread-3', 'facebook', 'bot', 'Bot', 'We sincerely apologize for your experience. Can we make it right?', two_days_ago)
        ]
        
        for thread_id, platform, sender_id, sender_name, text, timestamp in messages:
            cursor.execute("""
                INSERT INTO messages (thread_id, platform, sender_id, sender_name, text, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (thread_id, platform, sender_id, sender_name, text, timestamp))
            counts['messages'] += 1
        
        # Insert 2 leads linked to threads (source_platform instead of source)
        leads = [
            ('Lina', 'new', 'instagram', 'demo-thread-1', 'Interested in hair appointment and bridal makeup', 'beauty,bridal', None),
            ('Ahmed', 'contacted', 'whatsapp', 'demo-thread-2', 'Inquired about facial treatment pricing', 'facial,interested', None)
        ]
        
        for name, status, source_platform, thread_id, notes, tags, phone in leads:
            cursor.execute("""
                INSERT INTO leads (name, status, source_platform, thread_id, notes, tags, phone, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, status, source_platform, thread_id, notes, tags, phone, now, now))
            lead_id = cursor.lastrowid
            counts['leads'] += 1
            
            # Create tasks for leads
            if name == 'Lina':
                # Overdue task
                overdue_time = (datetime.utcnow() - timedelta(days=1)).isoformat()
                cursor.execute("""
                    INSERT INTO tasks (title, type, completed, due_at, related_lead_id, related_thread_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (f'Follow up with {name}', 'followup', 0, overdue_time, lead_id, thread_id, now))
                counts['tasks'] += 1
            
            elif name == 'Ahmed':
                # Due today
                today_time = (datetime.utcnow() + timedelta(hours=6)).isoformat()
                cursor.execute("""
                    INSERT INTO tasks (title, type, completed, due_at, related_lead_id, related_thread_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (f'Send booking options to {name}', 'followup', 0, today_time, lead_id, thread_id, now))
                counts['tasks'] += 1
        
        # Add one upcoming task (not linked to lead)
        tomorrow_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
        cursor.execute("""
            INSERT INTO tasks (title, type, completed, due_at, related_lead_id, related_thread_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('Review negative feedback and respond', 'followup', 0, tomorrow_time, None, 'demo-thread-3', now))
        counts['tasks'] += 1
        
        # Seed saved replies (only if none exist)
        cursor.execute("SELECT COUNT(*) FROM replies")
        existing_replies = cursor.fetchone()[0]
        
        if existing_replies == 0:
            replies = [
                ('Greeting', 'Hello! Thank you for reaching out. How can I help you today?', 'en', 'greeting'),
                ('Booking Confirmation', 'Your appointment has been confirmed for {date} at {time}. See you soon!', 'en', 'booking'),
                ('Price Info', 'Our services range from 100-500 AED. Would you like a detailed price list?', 'en', 'pricing'),
                ('Apology', 'We sincerely apologize for any inconvenience. Your satisfaction is our priority.', 'en', 'support'),
                ('تحية', 'مرحباً! شكراً لتواصلك معنا. كيف يمكنني مساعدتك اليوم؟', 'ar', 'greeting')
            ]
            
            for title, body, lang, tags in replies:
                cursor.execute("""
                    INSERT INTO replies (title, body, lang, tags, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (title, body, lang, tags, now, now))
                counts['replies'] += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f"Demo data seeded: {counts}")
        return counts
    
    except Exception as e:
        logger.error(f"Demo seed error: {e}", exc_info=True)
        return {'error': str(e), 'skipped': False}
