"""
Salons Plugin - Example implementation for SocialOps Agent Core.

Demonstrates how to implement the Plugin interface for a salon booking use case.
Supports 10 intent types with template-based replies in English and Arabic.
"""

from typing import Dict, Any, Set
import logging
import random

from plugins._base import Plugin
from plugins.salons.intents import classify_intent, extract_entities

logger = logging.getLogger(__name__)

# Embedded templates - no external dependencies
TEMPLATES = {
    "en": {
        "booking": [
            "Thanks for your interest! I'd love to help book an appointment. Can you tell me your preferred date and time?",
            "Great! We have availability for {service}. When would you like to come in? Please share your preferred date and time.",
            "Excellent! To book your appointment, I'll need: 1) Service type, 2) Preferred date, 3) Preferred time. What works best for you?"
        ],
        "prices": [
            "Thank you for asking about pricing! Our services range from AED 100 to AED 500 depending on the treatment. Which specific service interests you?",
            "I'd be happy to share pricing details. Our main services: Hair styling (AED 150-350), Makeup (AED 250-500), Nails (AED 100-200). Which would you like to know more about?",
            "Our pricing varies by service. Could you tell me which treatment you're interested in? I'll give you the specific prices and available packages."
        ],
        "location": [
            "We're located at {location}. You can easily find us on Google Maps or Waze. Looking forward to seeing you!",
            "Our salon is at {location}. We're easy to reach with parking available. Would you like directions?",
            "You can find us at {location}. For detailed directions, please call us at {phone} or check the map link in our profile."
        ],
        "hours": [
            "We're open Sunday to Thursday: 9 AM - 8 PM, Friday: 2 - 9 PM, Closed Saturday. Which day works for you?",
            "Our hours are 9 AM to 8 PM on weekdays, and 2 - 9 PM on Friday. Closed Saturday. When would you like to visit?",
            "Thanks for asking! We operate: Sunday-Thursday (9 AM - 8 PM), Friday (2 - 9 PM), Closed Saturday. Is there a specific time that suits you?"
        ],
        "services": [
            "We offer a full range of beauty services including: hair styling and coloring, professional makeup, nail care, bridal packages, and special occasion styling. What interests you?",
            "Our services include: Hair care (cut, color, treatments), Makeup artistry, Nail services, Bridal packages & special events. Which service would you like to know more about?",
            "We specialize in: Hair services, Makeup (daily & bridal), Nails (mani/pedi), and special packages for occasions. How can we help you look your best?"
        ],
        "reschedule": [
            "No problem! I can help you reschedule. Could you provide: 1) Your current appointment date/time, 2) Your new preferred date/time?",
            "Of course, we can reschedule your appointment. Please share your booking details and when you'd prefer to reschedule.",
            "Happy to help with rescheduling. What's your current appointment, and what new date/time works better for you?"
        ],
        "cancellation": [
            "We understand plans change. You can cancel up to 24 hours before your appointment for a full refund. Cancellations within 24 hours incur a 50% fee. Would you prefer to cancel or reschedule?",
            "Our cancellation policy: Free cancellation 24+ hours before appointment. Cancellations within 24 hours subject to 50% fee. Can I help you reschedule instead?",
            "Cancellation possible with: 100% refund if 24+ hours notice, 50% fee if within 24 hours. You can also reschedule with no fee. What would you prefer?"
        ],
        "complaint": [
            "I sincerely apologize for your experience. This is not the level of service we strive for. Could you share more details so I can escalate this to our manager? Your satisfaction is our priority.",
            "I'm truly sorry about your negative experience. We take all feedback seriously. I'd like to escalate this immediately to our management team. Can I get more details to help resolve this?",
            "My sincere apologies for the inconvenience. This doesn't reflect our values. I'm escalating your concern to our manager who will contact you directly at {phone}. Thank you for bringing this to our attention."
        ],
        "confirmation": [
            "Perfect! Your appointment is confirmed for {date} at {time} for {service}. We'll send you a reminder 24 hours ahead. Looking forward to seeing you!",
            "Great! Booking confirmed: {service} on {date} at {time}. Please arrive 5 minutes early. See you soon!",
            "All set! Your appointment for {service} is booked for {date} at {time}. You'll receive a confirmation message shortly. Can't wait to serve you!"
        ],
        "upsell": [
            "Would you like to enhance your experience? We're currently offering: Premium hair treatment (+AED 70), Quick makeup touch-up (+AED 50). Interested?",
            "Since you're booking {service}, many clients also add: Deep conditioning treatment, French manicure, or makeup application. Would you like to add any?",
            "Special offer: Add any additional service to your {service} appointment and get 20% off the second service! Popular add-ons: Nails, Makeup, Hair treatment. Interested?"
        ]
    },
    "ar": {
        "booking": [
            "شكراً لاهتمامك! يسعدني مساعدتك في حجز موعد. هل يمكنك إخباري بالتاريخ والوقت المفضل لك؟",
            "رائع! لدينا مواعيد متاحة لخدمة {service}. متى تفضلين الحضور؟ يرجى مشاركة التاريخ والوقت المناسب.",
            "ممتاز! لحجز موعدك، سأحتاج: 1) نوع الخدمة، 2) التاريخ المفضل، 3) الوقت المفضل. ما الأنسب لك؟"
        ],
        "prices": [
            "شكراً لسؤالك عن الأسعار! خدماتنا تتراوح بين 100 إلى 500 درهم حسب العلاج. أي خدمة تهمك تحديداً؟",
            "يسعدنا تقديم تفاصيل الأسعار. خدماتنا الرئيسية: تصفيف الشعر (150-350 درهم)، المكياج (250-500 درهم)، الأظافر (100-200 درهم). عن أي خدمة تريدين معرفة المزيد؟",
            "أسعارنا تختلف حسب الخدمة. هل يمكنك إخباري بالعلاج الذي يهمك؟ سأقدم لك الأسعار المحددة والباقات المتاحة."
        ],
        "location": [
            "موقعنا في {location}. يمكنك إيجادنا بسهولة عبر خرائط جوجل أو Waze. نتطلع لرؤيتك!",
            "صالوننا يقع في {location}. موقعنا سهل الوصول مع توفر مواقف سيارات. هل تريدين الاتجاهات؟",
            "يمكنك إيجادنا في {location}. للحصول على اتجاهات تفصيلية، يرجى الاتصال بنا على {phone} أو مراجعة رابط الخريطة في ملفنا الشخصي."
        ],
        "hours": [
            "نحن مفتوحون الأحد إلى الخميس: 9 صباحاً - 8 مساءً، الجمعة: 2 - 9 مساءً، مغلق السبت. أي يوم يناسبك؟",
            "ساعات عملنا من 9 صباحاً حتى 8 مساءً في أيام الأسبوع، ومن 2 - 9 مساءً يوم الجمعة. مغلق يوم السبت. متى تفضلين الزيارة؟",
            "شكراً لسؤالك! نعمل: الأحد-الخميس (9 صباحاً - 8 مساءً)، الجمعة (2 - 9 مساءً)، مغلق السبت. هل هناك وقت معين يناسبك؟"
        ],
        "services": [
            "نقدم مجموعة كاملة من خدمات التجميل بما في ذلك: تصفيف وصبغ الشعر، المكياج الاحترافي، العناية بالأظافر، باقات العرائس، وتسريحات المناسبات. ماذا يهمك؟",
            "خدماتنا تشمل: العناية بالشعر (قص، صبغ، علاجات)، فن المكياج، خدمات الأظافر، باقات العرائس والمناسبات. أي خدمة تريدين معرفة المزيد عنها؟",
            "نحن متخصصون في: خدمات الشعر، المكياج (يومي وعرائس)، الأظافر (مانيكير/باديكير)، وباقات خاصة للمناسبات. كيف يمكننا مساعدتك لتبدي بأفضل إطلالة؟"
        ],
        "reschedule": [
            "لا مشكلة! يمكنني مساعدتك في إعادة الجدولة. هل يمكنك تقديم: 1) تاريخ/وقت موعدك الحالي، 2) التاريخ/الوقت الجديد المفضل؟",
            "بالطبع، يمكننا إعادة جدولة موعدك. يرجى مشاركة تفاصيل حجزك ومتى تفضلين إعادة الجدولة.",
            "يسعدني المساعدة في إعادة الجدولة. ما هو موعدك الحالي، وما التاريخ/الوقت الجديد الأنسب لك؟"
        ],
        "cancellation": [
            "نتفهم أن الخطط قد تتغير. يمكنك الإلغاء قبل 24 ساعة من موعدك للحصول على استرداد كامل. للإلغاء خلال 24 ساعة، تطبق رسوم 50%. هل تفضلين الإلغاء أم إعادة الجدولة؟",
            "سياسة الإلغاء لدينا: إلغاء مجاني قبل 24+ ساعة من الموعد. الإلغاء خلال 24 ساعة يخضع لرسوم 50%. هل يمكنني مساعدتك في إعادة الجدولة؟",
            "الإلغاء ممكن مع: استرداد 100% إذا كان قبل 24+ ساعة، رسوم 50% إذا كان خلال 24 ساعة. يمكنك أيضاً إعادة الجدولة بدون رسوم. ماذا تفضلين؟"
        ],
        "complaint": [
            "أعتذر بشدة عن تجربتك. هذا ليس مستوى الخدمة الذي نهدف إليه. هل يمكنك مشاركة المزيد من التفاصيل حتى أتمكن من إحالة هذا الأمر إلى مديرنا؟ رضاك أولويتنا.",
            "أنا آسفة حقاً لتجربتك السلبية. نأخذ كل الملاحظات على محمل الجد. أود إحالة هذا فوراً إلى فريق الإدارة لدينا. هل يمكنني الحصول على المزيد من التفاصيل للمساعدة في حل هذا؟",
            "اعتذاري الصادق عن الإزعاج. هذا لا يعكس قيمنا. أقوم بإحالة مشكلتك إلى مديرنا الذي سيتصل بك مباشرة على {phone}. شكراً لإحضار هذا إلى انتباهنا."
        ],
        "confirmation": [
            "ممتاز! موعدك مؤكد ليوم {date} في الساعة {time} لخدمة {service}. سنرسل لك تذكيراً قبل 24 ساعة. نتطلع لرؤيتك!",
            "رائع! الحجز مؤكد: {service} في {date} الساعة {time}. يرجى الحضور قبل 5 دقائق. نراك قريباً!",
            "تم الإعداد! موعدك لخدمة {service} محجوز ليوم {date} في الساعة {time}. ستستلمين رسالة تأكيد قريباً. لا يمكننا الانتظار لخدمتك!"
        ],
        "upsell": [
            "هل تودين تحسين تجربتك؟ نقدم حالياً: علاج شعر مميز (+70 درهم)، لمسة مكياج سريعة (+50 درهم). مهتمة؟",
            "بما أنك تحجزين {service}، العديد من العميلات يضفن أيضاً: علاج ترطيب عميق، مانيكير فرنسي، أو تطبيق مكياج. هل تودين إضافة أي منها؟",
            "عرض خاص: أضيفي أي خدمة إضافية إلى موعد {service} واحصلي على خصم 20% على الخدمة الثانية! الإضافات الشائعة: الأظافر، المكياج، علاج الشعر. مهتمة؟"
        ]
    }
}


class SalonsPlugin(Plugin):
    """
    Salons booking plugin - Example implementation.
    
    Handles 10 intent types:
    1. booking - Appointment booking requests
    2. prices - Pricing inquiries
    3. location - Location/address questions
    4. hours - Operating hours questions
    5. services - Service offerings questions
    6. reschedule - Appointment rescheduling
    7. cancellation - Cancellation policy questions
    8. complaint - Customer complaints
    9. confirmation - Booking confirmations
    10. upsell - Additional service offers
    """
    
    def __init__(self):
        """Initialize salons plugin with embedded templates."""
        self._name = "salons"
        self._platforms = {"instagram", "facebook", "whatsapp"}
        self.templates = TEMPLATES
        logger.info("SalonsPlugin initialized with embedded templates")
    
    @property
    def name(self) -> str:
        """Plugin identifier."""
        return self._name
    
    @property
    def supported_platforms(self) -> Set[str]:
        """Platforms this plugin supports."""
        return self._platforms
    
    def classify(self, text: str, lang: str) -> str:
        """
        Classify user message intent.
        
        Args:
            text: User message text
            lang: Language code ('en', 'ar')
            
        Returns:
            Intent string (booking, prices, etc.) or 'other'
        """
        intent = classify_intent(text, lang)
        logger.debug(f"Classified '{text[:30]}...' as '{intent}'")
        return intent
    
    def extract(self, text: str, lang: str) -> Dict[str, Any]:
        """
        Extract structured entities from message.
        
        Args:
            text: User message text
            lang: Language code
            
        Returns:
            Dictionary of extracted entities (date, time, service, name, etc.)
        """
        entities = extract_entities(text, lang)
        logger.debug(f"Extracted entities: {entities}")
        return entities
    
    def suggest_reply(self, intent: str, lang: str, context: Dict[str, Any]) -> str:
        """
        Generate reply suggestion using templates.
        
        Args:
            intent: Classified intent
            lang: Language code ('en', 'ar')
            context: Context including extracted entities, sender_name, etc.
            
        Returns:
            Suggested reply text
        """
        # Get templates for language
        lang_templates = self.templates.get(lang, {})
        
        if not lang_templates:
            # Fallback to English if language not found
            lang_templates = self.templates.get('en', {})
            logger.warning(f"No templates for lang '{lang}', using English")
        
        # Get templates for intent
        intent_templates = lang_templates.get(intent, [])
        
        if not intent_templates:
            # Fallback to generic response
            if lang == 'ar':
                return "شكراً على رسالتك! سنساعدك قريباً."
            else:
                return "Thank you for your message! We'll assist you shortly."
        
        # Select random template
        template = random.choice(intent_templates)
        
        # Fill in placeholders with context data
        reply = self._fill_template(template, context)
        
        logger.debug(f"Generated reply for intent '{intent}': {reply[:50]}...")
        return reply
    
    def _fill_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Fill template placeholders with context data.
        
        Args:
            template: Template string with placeholders like {name}, {date}
            context: Context dictionary
            
        Returns:
            Filled template
        """
        # Extract entities and other context
        extracted = context.get('extracted', {})
        sender_name = context.get('sender_name', '')
        
        # Build replacement dict
        replacements = {
            'name': sender_name,
            'date': extracted.get('day', 'your preferred date'),
            'time': extracted.get('time', 'your preferred time'),
            'service': extracted.get('service', 'the service'),
            'location': '123 Main Street, Dubai',  # Could be from config
            'phone': '+971-XX-XXX-XXXX',  # Could be from config
        }
        
        # Replace placeholders
        result = template
        for key, value in replacements.items():
            result = result.replace(f'{{{key}}}', str(value))
        
        return result
