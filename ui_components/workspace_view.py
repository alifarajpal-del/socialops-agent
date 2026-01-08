"""
Workspace View - Business profile management UI.

Provides form to edit workspace/business identity.
"""

import streamlit as st
import logging

from services.workspace_store import WorkspaceStore
from ui_components import ui_kit
from utils.i18n import get_lang
from utils.translations import get_text

logger = logging.getLogger(__name__)


def workspace_view():
    """Main workspace profile view."""
    try:
        ui_kit.inject_ui_kit_css()
        
        lang = get_lang()
        
        # Header
        st.title(f"🏢 {get_text('workspace_title', lang)}")
        st.caption(get_text('workspace_caption', lang))
        
        st.divider()
        
        # Get workspace store
        workspace_store = WorkspaceStore()
        profile = workspace_store.get_profile() or {}
        
        # Edit form
        with st.form(key="workspace_profile_form"):
            st.markdown(f"### {get_text('workspace_title', lang)}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                business_name = st.text_input(
                    get_text('business_name', lang),
                    value=profile.get('business_name', ''),
                    placeholder="E.g., Lina's Beauty Salon"
                )
                
                business_type = st.selectbox(
                    get_text('business_type', lang),
                    options=["salon", "clinic", "restaurant", "retail", "service", "other"],
                    index=["salon", "clinic", "restaurant", "retail", "service", "other"].index(
                        profile.get('business_type', 'salon')
                    ) if profile.get('business_type') in ["salon", "clinic", "restaurant", "retail", "service", "other"] else 0,
                    format_func=lambda x: x.capitalize()
                )
                
                city = st.text_input(
                    get_text('city', lang),
                    value=profile.get('city', ''),
                    placeholder="E.g., Dubai"
                )
                
                phone = st.text_input(
                    get_text('phone', lang),
                    value=profile.get('phone', ''),
                    placeholder="E.g., +971 50 123 4567"
                )
            
            with col2:
                hours = st.text_input(
                    get_text('hours', lang),
                    value=profile.get('hours', ''),
                    placeholder="E.g., 9AM-9PM daily"
                )
                
                booking_link = st.text_input(
                    get_text('booking_link', lang),
                    value=profile.get('booking_link', ''),
                    placeholder="E.g., https://book.me/lina"
                )
                
                location_link = st.text_input(
                    get_text('location_link', lang),
                    value=profile.get('location_link', ''),
                    placeholder="E.g., https://maps.google.com/..."
                )
                
                brand_tone = st.selectbox(
                    get_text('brand_tone', lang),
                    options=["friendly", "professional"],
                    index=["friendly", "professional"].index(
                        profile.get('brand_tone', 'friendly')
                    ),
                    format_func=lambda x: x.capitalize()
                )
            
            lang_default = st.selectbox(
                get_text('lang_default', lang),
                options=["en", "ar", "fr"],
                index=["en", "ar", "fr"].index(profile.get('lang_default', 'en')),
                format_func=lambda x: {"en": "English", "ar": "العربية", "fr": "Français"}[x]
            )
            
            submitted = st.form_submit_button("💾 Save Profile", use_container_width=True, type="primary")
            
            if submitted:
                # Save profile
                workspace_store.save_profile({
                    'business_name': business_name,
                    'business_type': business_type,
                    'city': city,
                    'phone': phone,
                    'hours': hours,
                    'booking_link': booking_link,
                    'location_link': location_link,
                    'brand_tone': brand_tone,
                    'lang_default': lang_default
                })
                st.success("✅ Profile saved!")
                st.rerun()
        
        # Show preview
        if profile:
            st.divider()
            with ui_kit.card(title="Profile Preview", icon="👁️"):
                st.markdown(f"**{profile.get('business_name', 'N/A')}**")
                st.caption(f"{profile.get('business_type', 'N/A').capitalize()} · {profile.get('city', 'N/A')}")
                
                if profile.get('phone'):
                    st.text(f"📞 {profile['phone']}")
                
                if profile.get('hours'):
                    st.text(f"🕐 {profile['hours']}")
                
                if profile.get('booking_link'):
                    st.markdown(f"🔗 [Book Now]({profile['booking_link']})")
                
                if profile.get('location_link'):
                    st.markdown(f"📍 [View Location]({profile['location_link']})")
    
    except Exception as e:
        logger.error(f"Workspace view error: {e}", exc_info=True)
        st.error(f"Error loading workspace: {str(e)}")
