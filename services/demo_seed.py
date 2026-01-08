"""
Demo Seed Service - Populate database with sample data for testing.

Provides idempotent demo data seeding for inbox, CRM, and replies.
Seeds 9 threads across 3 sectors: salon, store, clinic.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional

from services.db import get_db_path

logger = logging.getLogger(__name__)


def _is_demo_id(value: str) -> bool:
    """Check if a value is a demo identifier."""
    if not value:
        return False
    return any(pattern in value for pattern in ['demo_salon_', 'demo_store_', 'demo_clinic_'])


def infer_sector_from_thread_id(thread_id: str) -> str:
    """
    Infer sector from thread_id prefix.
    
    Args:
        thread_id: Thread identifier string
    
    Returns:
        "salon", "store", "clinic", or "unknown"
    """
    if not thread_id:
        return "unknown"
    
    thread_id_lower = thread_id.lower()
    
    if 'salon' in thread_id_lower:
        return "salon"
    elif 'store' in thread_id_lower:
        return "store"
    elif 'clinic' in thread_id_lower:
        return "clinic"
    else:
        return "unknown"


def demo_exists(db_path: Optional[str] = None) -> bool:
    """
    Check if any demo data exists in the database.
    
    Args:
        db_path: Optional database path (uses get_db_path() if None)
    
    Returns:
        True if any demo thread exists, False otherwise
    """
    if db_path is None:
        db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM threads 
            WHERE thread_id LIKE 'demo_salon_%' 
               OR thread_id LIKE 'demo_store_%' 
               OR thread_id LIKE 'demo_clinic_%'
        """)
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    except Exception as e:
        logger.error(f"Error checking demo existence: {e}", exc_info=True)
        return False


def get_demo_stats(db_path: Optional[str] = None) -> dict:
    """
    Get statistics about demo data in the database.
    
    Safe to call on empty database.
    
    Args:
        db_path: Optional database path (uses get_db_path() if None)
    
    Returns:
        Dict with structure: {
            "exists": bool,
            "threads": int,
            "leads": int,
            "tasks": int,
            "replies": int
        }
    """
    if db_path is None:
        db_path = get_db_path()
    
    stats = {
        'exists': False,
        'threads': 0,
        'leads': 0,
        'tasks': 0,
        'replies': 0
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count demo threads
        cursor.execute("""
            SELECT COUNT(*) FROM threads 
            WHERE thread_id LIKE 'demo_salon_%' 
               OR thread_id LIKE 'demo_store_%' 
               OR thread_id LIKE 'demo_clinic_%'
        """)
        stats['threads'] = cursor.fetchone()[0]
        
        # Count demo leads (linked by thread_id)
        cursor.execute("""
            SELECT COUNT(*) FROM leads 
            WHERE thread_id LIKE 'demo_salon_%' 
               OR thread_id LIKE 'demo_store_%' 
               OR thread_id LIKE 'demo_clinic_%'
        """)
        stats['leads'] = cursor.fetchone()[0]
        
        # Count demo tasks (linked by related_thread_id)
        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE related_thread_id LIKE 'demo_salon_%' 
               OR related_thread_id LIKE 'demo_store_%' 
               OR related_thread_id LIKE 'demo_clinic_%'
        """)
        stats['tasks'] = cursor.fetchone()[0]
        
        # Count demo replies (identified by tags)
        cursor.execute("""
            SELECT COUNT(*) FROM replies 
            WHERE tags LIKE '%salon%' 
               OR tags LIKE '%store%' 
               OR tags LIKE '%clinic%'
        """)
        stats['replies'] = cursor.fetchone()[0]
        
        conn.close()
        
        stats['exists'] = stats['threads'] > 0
        
        return stats
    except Exception as e:
        logger.error(f"Error getting demo stats: {e}", exc_info=True)
        return stats


def seed_demo_all(db_path: Optional[str] = None) -> dict:
    """
    Seed database with demo data for all sectors (salon, store, clinic).
    
    Idempotent: Checks if demo data already exists before inserting.
    
    Args:
        db_path: Optional database path (uses get_db_path() if None)
    
    Returns:
        Dict with structure: {
            "created": bool,
            "threads": int,
            "messages": int,
            "leads": int,
            "tasks": int,
            "replies": int,
            "skipped": bool,
            "reason": str | None
        }
    """
    if db_path is None:
        db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        counts = {
            'created': False,
            'threads': 0,
            'messages': 0,
            'leads': 0,
            'tasks': 0,
            'replies': 0,
            'skipped': False,
            'reason': None
        }
        
        # Check if any demo data already exists
        cursor.execute("""
            SELECT COUNT(*) FROM threads 
            WHERE thread_id LIKE 'demo_salon_%' 
               OR thread_id LIKE 'demo_store_%' 
               OR thread_id LIKE 'demo_clinic_%'
        """)
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            logger.info(f"Demo data already exists ({existing_count} threads), skipping seed")
            counts['skipped'] = True
            counts['reason'] = f"Demo data already exists ({existing_count} threads)"
            conn.close()
            return counts
        
        # Seed all sectors
        now = datetime.utcnow().isoformat()
        
        _seed_salon(conn, cursor, counts, now)
        _seed_store(conn, cursor, counts, now)
        _seed_clinic(conn, cursor, counts, now)
        
        conn.commit()
        conn.close()
        
        counts['created'] = True
        logger.info(f"Demo data seeded: {counts}")
        return counts
    
    except Exception as e:
        logger.error(f"Demo seed error: {e}", exc_info=True)
        return {'error': str(e), 'created': False, 'skipped': False, 'reason': str(e)}


def clear_demo_all(db_path: Optional[str] = None) -> dict:
    """
    Delete ALL demo data created by seeding across all 3 sectors.
    
    Removes demo threads, related messages, related leads, related tasks,
    and demo saved replies. Safe if called when no demo exists.
    
    Args:
        db_path: Optional database path (uses get_db_path() if None)
    
    Returns:
        Dict with structure: {
            "cleared": bool,
            "threads_deleted": int,
            "messages_deleted": int,
            "leads_deleted": int,
            "tasks_deleted": int,
            "replies_deleted": int
        }
    """
    if db_path is None:
        db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        counts = {
            'cleared': False,
            'threads_deleted': 0,
            'messages_deleted': 0,
            'leads_deleted': 0,
            'tasks_deleted': 0,
            'replies_deleted': 0
        }
        
        # Delete messages first (foreign key to threads)
        cursor.execute("""
            DELETE FROM messages 
            WHERE thread_id LIKE 'demo_salon_%' 
               OR thread_id LIKE 'demo_store_%' 
               OR thread_id LIKE 'demo_clinic_%'
        """)
        counts['messages_deleted'] = cursor.rowcount
        
        # Delete leads linked to demo threads
        cursor.execute("""
            DELETE FROM leads 
            WHERE thread_id LIKE 'demo_salon_%' 
               OR thread_id LIKE 'demo_store_%' 
               OR thread_id LIKE 'demo_clinic_%'
        """)
        counts['leads_deleted'] = cursor.rowcount
        
        # Delete tasks linked to demo threads
        cursor.execute("""
            DELETE FROM tasks 
            WHERE related_thread_id LIKE 'demo_salon_%' 
               OR related_thread_id LIKE 'demo_store_%' 
               OR related_thread_id LIKE 'demo_clinic_%'
        """)
        counts['tasks_deleted'] = cursor.rowcount
        
        # Delete demo saved replies
        cursor.execute("""
            DELETE FROM replies 
            WHERE tags LIKE '%salon%' 
               OR tags LIKE '%store%' 
               OR tags LIKE '%clinic%'
        """)
        counts['replies_deleted'] = cursor.rowcount
        
        # Delete demo threads last
        cursor.execute("""
            DELETE FROM threads 
            WHERE thread_id LIKE 'demo_salon_%' 
               OR thread_id LIKE 'demo_store_%' 
               OR thread_id LIKE 'demo_clinic_%'
        """)
        counts['threads_deleted'] = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        counts['cleared'] = True
        logger.info(f"Demo data cleared: {counts}")
        return counts
    
    except Exception as e:
        logger.error(f"Demo clear error: {e}", exc_info=True)
        return {'error': str(e), 'cleared': False}


def seed_demo_regenerate(db_path: Optional[str] = None) -> dict:
    """
    Regenerate demo data: clear existing demo data then seed fresh data.
    
    This is a convenience function that calls clear_demo_all() followed by
    seed_demo_all() to provide a fresh demo dataset.
    
    Args:
        db_path: Optional database path (uses get_db_path() if None)
    
    Returns:
        Dict with structure: {
            "cleared": {...},
            "seeded": {...}
        }
    """
    if db_path is None:
        db_path = get_db_path()
    
    logger.info("Regenerating demo data (clear + seed)")
    
    # First clear
    clear_result = clear_demo_all(db_path)
    
    # Then seed
    seed_result = seed_demo_all(db_path)
    
    return {
        'cleared': clear_result,
        'seeded': seed_result
    }


def demo_integrity_check(db_path: Optional[str] = None) -> dict:
    """
    Check for orphaned demo data (records referencing missing demo threads).
    
    Scans for demo messages, leads, tasks, and replies that reference
    non-existent demo threads and optionally removes them.
    
    Args:
        db_path: Optional database path (uses get_db_path() if None)
    
    Returns:
        Dict with structure: {
            "orphans_found": int,
            "orphans_deleted": int,
            "details": {
                "orphan_messages": int,
                "orphan_leads": int,
                "orphan_tasks": int,
                "orphan_replies": int (estimate)
            }
        }
    """
    if db_path is None:
        db_path = get_db_path()
    
    result = {
        'orphans_found': 0,
        'orphans_deleted': 0,
        'details': {
            'orphan_messages': 0,
            'orphan_leads': 0,
            'orphan_tasks': 0,
            'orphan_replies': 0
        }
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all valid demo thread IDs
        cursor.execute("""
            SELECT thread_id FROM threads 
            WHERE thread_id LIKE 'demo_salon_%' 
               OR thread_id LIKE 'demo_store_%' 
               OR thread_id LIKE 'demo_clinic_%'
        """)
        valid_threads = set(row[0] for row in cursor.fetchall())
        
        if not valid_threads:
            # No demo threads exist, so we can clean all demo-related records
            logger.info("No demo threads found, cleaning all demo records")
            
            # Count and delete orphan messages
            cursor.execute("""
                SELECT COUNT(*) FROM messages 
                WHERE thread_id LIKE 'demo_%'
            """)
            orphan_messages = cursor.fetchone()[0]
            
            if orphan_messages > 0:
                cursor.execute("DELETE FROM messages WHERE thread_id LIKE 'demo_%'")
                result['details']['orphan_messages'] = orphan_messages
                result['orphans_deleted'] += orphan_messages
            
            # Count and delete orphan leads
            cursor.execute("""
                SELECT COUNT(*) FROM leads 
                WHERE thread_id LIKE 'demo_%'
            """)
            orphan_leads = cursor.fetchone()[0]
            
            if orphan_leads > 0:
                cursor.execute("DELETE FROM leads WHERE thread_id LIKE 'demo_%'")
                result['details']['orphan_leads'] = orphan_leads
                result['orphans_deleted'] += orphan_leads
            
            # Count and delete orphan tasks
            cursor.execute("""
                SELECT COUNT(*) FROM tasks 
                WHERE related_thread_id LIKE 'demo_%'
            """)
            orphan_tasks = cursor.fetchone()[0]
            
            if orphan_tasks > 0:
                cursor.execute("DELETE FROM tasks WHERE related_thread_id LIKE 'demo_%'")
                result['details']['orphan_tasks'] = orphan_tasks
                result['orphans_deleted'] += orphan_tasks
            
            result['orphans_found'] = orphan_messages + orphan_leads + orphan_tasks
            
        else:
            # Check for orphans (demo records referencing non-existent threads)
            for table, id_column in [
                ('messages', 'thread_id'),
                ('leads', 'thread_id'),
                ('tasks', 'related_thread_id')
            ]:
                cursor.execute(f"""
                    SELECT {id_column} FROM {table}
                    WHERE {id_column} LIKE 'demo_%'
                """)
                
                orphan_count = 0
                for row in cursor.fetchall():
                    ref_id = row[0]
                    if ref_id not in valid_threads and _is_demo_id(ref_id):
                        orphan_count += 1
                
                if orphan_count > 0:
                    # Delete orphans
                    placeholders = ','.join(['?' for _ in valid_threads])
                    cursor.execute(f"""
                        DELETE FROM {table}
                        WHERE {id_column} LIKE 'demo_%'
                        AND {id_column} NOT IN ({placeholders})
                    """, list(valid_threads))
                    
                    table_key = f'orphan_{table}'
                    result['details'][table_key] = orphan_count
                    result['orphans_deleted'] += orphan_count
                    result['orphans_found'] += orphan_count
        
        conn.commit()
        conn.close()
        
        logger.info(f"Integrity check complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Integrity check error: {e}", exc_info=True)
        return {
            'error': str(e),
            'orphans_found': 0,
            'orphans_deleted': 0,
            'details': {}
        }


def _seed_salon(conn, cursor, counts, now):
    """Seed salon sector demo data (3 threads, 2 leads, 3 tasks, 5 replies)."""
    
    # Salon threads
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
    two_days = (datetime.utcnow() - timedelta(days=2)).isoformat()
    
    threads = [
        ('demo_salon_001', 'instagram', 'موعد قص شعر وصبغة', yesterday),
        ('demo_salon_002', 'whatsapp', 'استفسار عن ميك اب عرايس', now),
        ('demo_salon_003', 'facebook', 'شكوى من الخدمة', two_days)
    ]
    
    for thread_id, platform, title, timestamp in threads:
        cursor.execute("""
            INSERT INTO threads (thread_id, platform, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (thread_id, platform, title, timestamp, timestamp))
        counts['threads'] += 1
    
    # Salon messages (10 messages)
    messages = [
        ('demo_salon_001', 'instagram', 'user001', 'لينا', 'مرحبا، بدي موعد قص شعر يوم السبت، في مواعيد؟', yesterday),
        ('demo_salon_001', 'instagram', 'bot', 'Bot', 'أهلاً وسهلاً! حياكِ الله. رح نتواصل معكِ قريباً', yesterday),
        ('demo_salon_001', 'instagram', 'user001', 'لينا', 'وكمان بدي أصبغ شعري، عندكم أومبري؟', yesterday),
        
        ('demo_salon_002', 'whatsapp', 'user002', 'سارة', 'السلام عليكم، شو أسعار ميك اب العروس؟', now),
        ('demo_salon_002', 'whatsapp', 'bot', 'Bot', 'وعليكم السلام، ميك اب العروس من 300 دينار', now),
        ('demo_salon_002', 'whatsapp', 'user002', 'سارة', 'تمام، وإذا بدي تجربة قبل العرس؟', now),
        ('demo_salon_002', 'whatsapp', 'bot', 'Bot', 'التجربة مجانية مع الحجز 💕', now),
        
        ('demo_salon_003', 'facebook', 'user003', 'منى', 'جيت أمس وما عجبتني الخدمة، شعري صار متقصف 😢', two_days),
        ('demo_salon_003', 'facebook', 'bot', 'Bot', 'نعتذر منك كتير، ممكن نعوضك بجلسة علاج مجانية؟', two_days),
        ('demo_salon_003', 'facebook', 'user003', 'منى', 'طيب مقبول، بس ما بدي نفس المصففة', two_days)
    ]
    
    for thread_id, platform, sender_id, sender_name, text, timestamp in messages:
        cursor.execute("""
            INSERT INTO messages (thread_id, platform, sender_id, sender_name, text, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (thread_id, platform, sender_id, sender_name, text, timestamp))
        counts['messages'] += 1
    
    # Salon leads (2 leads)
    leads = [
        ('لينا', 'new', 'instagram', 'demo_salon_001', 'تبي قص وصبغة أومبري، موعد يوم السبت', 'قص,صبغة', '+962791234567'),
        ('سارة', 'contacted', 'whatsapp', 'demo_salon_002', 'استفسار ميك اب عروس، مهتمة بالتجربة', 'عروس,ميك اب', '+962797654321')
    ]
    
    for name, status, source_platform, thread_id, notes, tags, phone in leads:
        cursor.execute("""
            INSERT INTO leads (name, status, source_platform, thread_id, notes, tags, phone, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, status, source_platform, thread_id, notes, tags, phone, now, now))
        lead_id = cursor.lastrowid
        counts['leads'] += 1
        
        # Tasks for salon leads
        if name == 'لينا':
            overdue = (datetime.utcnow() - timedelta(days=1)).isoformat()
            cursor.execute("""
                INSERT INTO tasks (title, type, completed, due_at, related_lead_id, related_thread_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f'متابعة مع {name} - موعد قص', 'followup', 0, overdue, lead_id, thread_id, now))
            counts['tasks'] += 1
        elif name == 'سارة':
            today = (datetime.utcnow() + timedelta(hours=6)).isoformat()
            cursor.execute("""
                INSERT INTO tasks (title, type, completed, due_at, related_lead_id, related_thread_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f'إرسال تفاصيل باقات العروس ل{name}', 'followup', 0, today, lead_id, thread_id, now))
            counts['tasks'] += 1
    
    # One extra task (complaint followup)
    tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
    cursor.execute("""
        INSERT INTO tasks (title, type, completed, due_at, related_lead_id, related_thread_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('الرد على شكوى منى وحجز جلسة علاج', 'followup', 0, tomorrow, None, 'demo_salon_003', now))
    counts['tasks'] += 1
    
    # Salon replies (5 replies, only if not exist)
    cursor.execute("SELECT COUNT(*) FROM replies WHERE tags LIKE '%salon%'")
    if cursor.fetchone()[0] == 0:
        replies = [
            ('ترحيب صالون', 'مرحبا حبيبتي 💕 أهلاً وسهلاً فيكِ! كيف ممكن نساعدك اليوم؟', 'ar', 'salon,greeting'),
            ('مواعيد متاحة', 'عندنا مواعيد متاحة {يوم} الساعة {وقت}. بدك تحجزي؟', 'ar', 'salon,booking'),
            ('أسعار الصالون', 'أسعارنا: قص 15 دينار، صبغة 40-80 دينار، ميك اب 25 دينار. شو بدك بالضبط؟', 'ar', 'salon,pricing'),
            ('اعتذار خدمة', 'نعتذر منك كتير يا قمر 😢 رضاكِ أهم شي عنا. حابين نعوضك بجلسة مجانية', 'ar', 'salon,apology'),
            ('Salon Greeting EN', 'Hello dear! 💕 Welcome! How can we help you today?', 'en', 'salon,greeting')
        ]
        
        for title, body, lang, tags in replies:
            cursor.execute("""
                INSERT INTO replies (title, body, lang, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, body, lang, tags, now, now))
            counts['replies'] += 1


def _seed_store(conn, cursor, counts, now):
    """Seed store sector demo data (3 threads, 2 leads, 3 tasks, 5 replies)."""
    
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
    two_days = (datetime.utcnow() - timedelta(days=2)).isoformat()
    
    # Store threads
    threads = [
        ('demo_store_001', 'whatsapp', 'استفسار عن منتجات التنظيف', now),
        ('demo_store_002', 'instagram', 'طلب توصيل لمنطقة جديدة', yesterday),
        ('demo_store_003', 'facebook', 'شكوى تأخير الطلبية', two_days)
    ]
    
    for thread_id, platform, title, timestamp in threads:
        cursor.execute("""
            INSERT INTO threads (thread_id, platform, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (thread_id, platform, title, timestamp, timestamp))
        counts['threads'] += 1
    
    # Store messages (11 messages)
    messages = [
        ('demo_store_001', 'whatsapp', 'user011', 'أحمد', 'السلام عليكم، عندكم ديتول معقم؟', now),
        ('demo_store_001', 'whatsapp', 'bot', 'Bot', 'وعليكم السلام، أيوا عندنا كل أنواع ديتول', now),
        ('demo_store_001', 'whatsapp', 'user011', 'أحمد', 'كم سعر العبوة الكبيرة؟', now),
        ('demo_store_001', 'whatsapp', 'bot', 'Bot', 'العبوة ١ لتر ب ٣.٥ دينار', now),
        
        ('demo_store_002', 'instagram', 'user012', 'فاطمة', 'مرحبا، بتوصلوا على جبل اللويبدة؟', yesterday),
        ('demo_store_002', 'instagram', 'bot', 'Bot', 'أهلاً! أيوا بنوصل، توصيل مجاني فوق ٢٥ دينار', yesterday),
        ('demo_store_002', 'instagram', 'user012', 'فاطمة', 'تمام، بدي أطلب مواد تنظيف', yesterday),
        
        ('demo_store_003', 'facebook', 'user013', 'خالد', 'طلبيتي تأخرت ٣ أيام! وين الطلب؟', two_days),
        ('demo_store_003', 'facebook', 'bot', 'Bot', 'نعتذر على التأخير، رح نتأكد ونرد عليك', two_days),
        ('demo_store_003', 'facebook', 'user013', 'خالد', 'هاي آخر مرة أطلب منكم', two_days),
        ('demo_store_003', 'facebook', 'bot', 'Bot', 'نعتذر كتير، رح نعوضك برصيد ١٠ دنانير', two_days)
    ]
    
    for thread_id, platform, sender_id, sender_name, text, timestamp in messages:
        cursor.execute("""
            INSERT INTO messages (thread_id, platform, sender_id, sender_name, text, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (thread_id, platform, sender_id, sender_name, text, timestamp))
        counts['messages'] += 1
    
    # Store leads (2 leads)
    leads = [
        ('أحمد', 'new', 'whatsapp', 'demo_store_001', 'يسأل عن معقمات ديتول، مهتم بالشراء', 'تنظيف,معقم', '+962781234567'),
        ('فاطمة', 'contacted', 'instagram', 'demo_store_002', 'تبي توصيل لجبل اللويبدة، طلبية مواد تنظيف', 'توصيل,جديدة', '+962787654321')
    ]
    
    for name, status, source_platform, thread_id, notes, tags, phone in leads:
        cursor.execute("""
            INSERT INTO leads (name, status, source_platform, thread_id, notes, tags, phone, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, status, source_platform, thread_id, notes, tags, phone, now, now))
        lead_id = cursor.lastrowid
        counts['leads'] += 1
        
        # Tasks for store leads
        if name == 'أحمد':
            overdue = (datetime.utcnow() - timedelta(days=1)).isoformat()
            cursor.execute("""
                INSERT INTO tasks (title, type, completed, due_at, related_lead_id, related_thread_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f'إرسال كتالوج المعقمات ل{name}', 'followup', 0, overdue, lead_id, thread_id, now))
            counts['tasks'] += 1
        elif name == 'فاطمة':
            today = (datetime.utcnow() + timedelta(hours=6)).isoformat()
            cursor.execute("""
                INSERT INTO tasks (title, type, completed, due_at, related_lead_id, related_thread_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f'تأكيد عنوان التوصيل مع {name}', 'followup', 0, today, lead_id, thread_id, now))
            counts['tasks'] += 1
    
    # One extra task
    tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
    cursor.execute("""
        INSERT INTO tasks (title, type, completed, due_at, related_lead_id, related_thread_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('معالجة شكوى خالد وإضافة رصيد', 'followup', 0, tomorrow, None, 'demo_store_003', now))
    counts['tasks'] += 1
    
    # Store replies (5 replies)
    cursor.execute("SELECT COUNT(*) FROM replies WHERE tags LIKE '%store%'")
    if cursor.fetchone()[0] == 0:
        replies = [
            ('ترحيب متجر', 'أهلاً وسهلاً! 🛒 كيف ممكن نساعدك اليوم؟', 'ar', 'store,greeting'),
            ('توفر منتج', 'المنتج {اسم} متوفر عنا بسعر {سعر} دينار. حاب تطلبه؟', 'ar', 'store,availability'),
            ('شروط التوصيل', 'التوصيل مجاني لطلبات فوق ٢٥ دينار، بوصلك خلال ٢٤ ساعة', 'ar', 'store,delivery'),
            ('اعتذار تأخير', 'نعتذر كتير على التأخير 😔 رح نعوضك برصيد {مبلغ} دنانير', 'ar', 'store,apology'),
            ('Store Greeting EN', 'Welcome! 🛒 How can we help you today?', 'en', 'store,greeting')
        ]
        
        for title, body, lang, tags in replies:
            cursor.execute("""
                INSERT INTO replies (title, body, lang, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, body, lang, tags, now, now))
            counts['replies'] += 1


def _seed_clinic(conn, cursor, counts, now):
    """Seed clinic sector demo data (3 threads, 2 leads, 3 tasks, 5 replies)."""
    
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
    two_days = (datetime.utcnow() - timedelta(days=2)).isoformat()
    
    # Clinic threads
    threads = [
        ('demo_clinic_001', 'whatsapp', 'حجز موعد أسنان', now),
        ('demo_clinic_002', 'instagram', 'استفسار عن جلسات الليزر', yesterday),
        ('demo_clinic_003', 'facebook', 'شكوى انتظار طويل', two_days)
    ]
    
    for thread_id, platform, title, timestamp in threads:
        cursor.execute("""
            INSERT INTO threads (thread_id, platform, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (thread_id, platform, title, timestamp, timestamp))
        counts['threads'] += 1
    
    # Clinic messages (12 messages)
    messages = [
        ('demo_clinic_001', 'whatsapp', 'user021', 'نور', 'السلام عليكم، بدي موعد تنظيف أسنان', now),
        ('demo_clinic_001', 'whatsapp', 'bot', 'Bot', 'وعليكم السلام، عندنا موعد متاح يوم الخميس الساعة ٣ عصراً', now),
        ('demo_clinic_001', 'whatsapp', 'user021', 'نور', 'ممتاز، وكم السعر؟', now),
        ('demo_clinic_001', 'whatsapp', 'bot', 'Bot', 'تنظيف الأسنان ٣٥ دينار شامل الكشف', now),
        
        ('demo_clinic_002', 'instagram', 'user022', 'ريم', 'مرحبا، بدي أسأل عن ليزر إزالة الشعر', yesterday),
        ('demo_clinic_002', 'instagram', 'bot', 'Bot', 'أهلاً! عندنا جلسات ليزر ألماني، جلسة المنطقة ٧٥ دينار', yesterday),
        ('demo_clinic_002', 'instagram', 'user022', 'ريم', 'وإذا بدي باقة جسم كامل؟', yesterday),
        ('demo_clinic_002', 'instagram', 'bot', 'Bot', 'باقة ٨ جلسات جسم كامل ب ١٨٠٠ دينار بدل ٢٤٠٠', yesterday),
        
        ('demo_clinic_003', 'facebook', 'user023', 'سامي', 'جيت على موعدي وانتظرت ساعة! غير مقبول', two_days),
        ('demo_clinic_003', 'facebook', 'bot', 'Bot', 'نعتذر بشدة على التأخير، كان عنا طارئ', two_days),
        ('demo_clinic_003', 'facebook', 'user023', 'سامي', 'ما في احترام لوقت المريض', two_days),
        ('demo_clinic_003', 'facebook', 'bot', 'Bot', 'موعدك القادم مجاناً كتعويض، نعتذر مرة ثانية', two_days)
    ]
    
    for thread_id, platform, sender_id, sender_name, text, timestamp in messages:
        cursor.execute("""
            INSERT INTO messages (thread_id, platform, sender_id, sender_name, text, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (thread_id, platform, sender_id, sender_name, text, timestamp))
        counts['messages'] += 1
    
    # Clinic leads (2 leads)
    leads = [
        ('نور', 'new', 'whatsapp', 'demo_clinic_001', 'تبي تنظيف أسنان، موعد الخميس ٣ عصراً', 'أسنان,تنظيف', '+962771234567'),
        ('ريم', 'contacted', 'instagram', 'demo_clinic_002', 'مهتمة بباقة ليزر جسم كامل ٨ جلسات', 'ليزر,باقة', '+962777654321')
    ]
    
    for name, status, source_platform, thread_id, notes, tags, phone in leads:
        cursor.execute("""
            INSERT INTO leads (name, status, source_platform, thread_id, notes, tags, phone, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, status, source_platform, thread_id, notes, tags, phone, now, now))
        lead_id = cursor.lastrowid
        counts['leads'] += 1
        
        # Tasks for clinic leads
        if name == 'نور':
            overdue = (datetime.utcnow() - timedelta(days=1)).isoformat()
            cursor.execute("""
                INSERT INTO tasks (title, type, completed, due_at, related_lead_id, related_thread_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f'تأكيد موعد {name} - تنظيف أسنان', 'followup', 0, overdue, lead_id, thread_id, now))
            counts['tasks'] += 1
        elif name == 'ريم':
            today = (datetime.utcnow() + timedelta(hours=6)).isoformat()
            cursor.execute("""
                INSERT INTO tasks (title, type, completed, due_at, related_lead_id, related_thread_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f'إرسال تفاصيل باقات الليزر ل{name}', 'followup', 0, today, lead_id, thread_id, now))
            counts['tasks'] += 1
    
    # One extra task
    tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
    cursor.execute("""
        INSERT INTO tasks (title, type, completed, due_at, related_lead_id, related_thread_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('معالجة شكوى سامي وحجز موعد مجاني', 'followup', 0, tomorrow, None, 'demo_clinic_003', now))
    counts['tasks'] += 1
    
    # Clinic replies (5 replies)
    cursor.execute("SELECT COUNT(*) FROM replies WHERE tags LIKE '%clinic%'")
    if cursor.fetchone()[0] == 0:
        replies = [
            ('ترحيب عيادة', 'أهلاً وسهلاً 🏥 كيف ممكن نساعدك اليوم؟', 'ar', 'clinic,greeting'),
            ('حجز موعد', 'عندنا موعد متاح يوم {يوم} الساعة {وقت}. بدك تحجز؟', 'ar', 'clinic,appointment'),
            ('أسعار العيادة', 'أسعارنا: كشف {سعر١}، علاج {سعر٢}. شو العلاج المطلوب؟', 'ar', 'clinic,pricing'),
            ('اعتذار انتظار', 'نعتذر بشدة على الانتظار 🙏 موعدك القادم على حسابنا', 'ar', 'clinic,apology'),
            ('Clinic Greeting EN', 'Welcome! 🏥 How can we help you today?', 'en', 'clinic,greeting')
        ]
        
        for title, body, lang, tags in replies:
            cursor.execute("""
                INSERT INTO replies (title, body, lang, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, body, lang, tags, now, now))
            counts['replies'] += 1

