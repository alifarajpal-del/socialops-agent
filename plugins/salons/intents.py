"""
Intent classification and entity extraction for Salons plugin.
"""

import re
from typing import Dict, Any

# Intent keywords for classification
INTENT_KEYWORDS = {
    'booking': {
        'ar': ['حجز', 'موعد', 'أريد موعد', 'حجز موعد', 'تحديد موعد', 'احجز'],
        'en': ['book', 'appointment', 'schedule', 'reserve', 'booking', 'book me']
    },
    'prices': {
        'ar': ['سعر', 'أسعار', 'كم', 'تكلفة', 'ثمن', 'بكم'],
        'en': ['price', 'pricing', 'cost', 'how much', 'fee', 'rates']
    },
    'location': {
        'ar': ['موقع', 'عنوان', 'وين', 'فين', 'مكان'],
        'en': ['location', 'address', 'where', 'directions', 'map']
    },
    'hours': {
        'ar': ['ساعات', 'متى', 'وقت', 'مفتوح', 'مغلق', 'العمل'],
        'en': ['hours', 'open', 'close', 'opening', 'timing', 'schedule']
    },
    'services': {
        'ar': ['خدمة', 'خدمات', 'تقدم', 'تقدمون', 'عمل', 'ماذا'],
        'en': ['service', 'offer', 'provide', 'do you have', 'what services', 'menu']
    },
    'reschedule': {
        'ar': ['تغيير', 'تعديل', 'تأجيل', 'نقل', 'تبديل'],
        'en': ['reschedule', 'change', 'move', 'shift', 'modify']
    },
    'cancellation': {
        'ar': ['إلغاء', 'ألغي', 'سياسة', 'شروط'],
        'en': ['cancel', 'cancellation', 'policy', 'refund', 'terms']
    },
    'complaint': {
        'ar': ['شكوى', 'مشكلة', 'سيء', 'غير راضي', 'تأخير'],
        'en': ['complaint', 'problem', 'issue', 'bad', 'unhappy', 'delay']
    },
    'confirmation': {
        'ar': ['تأكيد', 'تم', 'موافق', 'نعم', 'صحيح'],
        'en': ['confirm', 'confirmed', 'yes', 'okay', 'correct', 'agreed']
    },
    'upsell': {
        'ar': ['إضافة', 'زيادة', 'أيضا', 'أخرى', 'معاها'],
        'en': ['add', 'also', 'additional', 'more', 'extra', 'upgrade']
    }
}


def classify_intent(text: str, lang: str) -> str:
    """
    Classify message intent using keyword matching.
    
    Args:
        text: User message text
        lang: Language code ('en', 'ar')
        
    Returns:
        Intent name or 'other' if no match
    """
    text_lower = text.lower()
    
    # Try to match keywords for each intent
    for intent, keywords in INTENT_KEYWORDS.items():
        lang_keywords = keywords.get(lang, []) + keywords.get('en', [])
        for keyword in lang_keywords:
            if keyword in text_lower:
                return intent
    
    return 'other'


def extract_entities(text: str, lang: str) -> Dict[str, Any]:
    """
    Extract structured entities from message.
    
    Args:
        text: User message text
        lang: Language code
        
    Returns:
        Dictionary of extracted entities
    """
    entities = {}
    text_lower = text.lower()
    
    # Extract day mentions (Arabic and English)
    day_patterns = {
        'ar': {
            'السبت': 'saturday', 'الأحد': 'sunday', 'الاثنين': 'monday',
            'الثلاثاء': 'tuesday', 'الأربعاء': 'wednesday',
            'الخميس': 'thursday', 'الجمعة': 'friday',
            'اليوم': 'today', 'غدا': 'tomorrow', 'بكرة': 'tomorrow'
        },
        'en': {
            'monday': 'monday', 'tuesday': 'tuesday', 'wednesday': 'wednesday',
            'thursday': 'thursday', 'friday': 'friday', 'saturday': 'saturday',
            'sunday': 'sunday', 'today': 'today', 'tomorrow': 'tomorrow'
        }
    }
    
    for day_text, day_name in day_patterns.get(lang, {}).items():
        if day_text in text_lower:
            entities['day'] = day_name
            break
    
    # Extract time patterns
    time_pattern = r'(\d{1,2}):(\d{2})|(\d{1,2})\s*(am|pm|صباحا|مساء)'
    time_match = re.search(time_pattern, text_lower)
    if time_match:
        entities['time'] = time_match.group(0)
    
    # Extract service mentions
    service_keywords = {
        'ar': ['شعر', 'مكياج', 'أظافر', 'صبغة', 'قص', 'تسريحة', 'عروس'],
        'en': ['hair', 'makeup', 'nails', 'color', 'cut', 'style', 'bridal']
    }
    
    for keyword in service_keywords.get(lang, []):
        if keyword in text_lower:
            entities['service'] = keyword
            break
    
    # Extract name patterns (basic)
    if lang == 'ar':
        name_pattern = r'اسمي\s+(\w+)|أنا\s+(\w+)'
    else:
        name_pattern = r"my name is\s+(\w+)|i'm\s+(\w+)|i am\s+(\w+)"
    
    name_match = re.search(name_pattern, text_lower)
    if name_match:
        for group in name_match.groups():
            if group:
                entities['name'] = group
                break
    
    return entities
