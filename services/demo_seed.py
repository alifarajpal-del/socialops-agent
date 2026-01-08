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


def seed_demo_all(db_path: Optional[str] = None) -> dict:
    """
    Seed database with demo data for all sectors (salon, store, clinic).
    
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
            conn.close()
            return counts
            return counts
        
        # Seed all sectors
        now = datetime.utcnow().isoformat()
        
        _seed_salon(conn, cursor, counts, now)
        _seed_store(conn, cursor, counts, now)
        _seed_clinic(conn, cursor, counts, now)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Demo data seeded: {counts}")
        return counts
    
    except Exception as e:
        logger.error(f"Demo seed error: {e}", exc_info=True)
        return {'error': str(e), 'skipped': False}


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

