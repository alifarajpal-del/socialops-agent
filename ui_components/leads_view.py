"""
Leads view for SocialOps AI Agent.
Display and manage customer leads with basic CRUD operations.
"""

import streamlit as st
from typing import Optional
from datetime import datetime
import logging

from services.leads import get_leads_manager, Lead, LeadStatus, LeadSource
from ui_components import ui_kit
from utils.i18n import t

logger = logging.getLogger(__name__)


def _get_status_badge(status: LeadStatus) -> str:
    """Get status badge HTML."""
    badge_map = {
        LeadStatus.NEW: ("New", "primary"),
        LeadStatus.CONTACTED: ("Contacted", "info"),
        LeadStatus.QUALIFIED: ("Qualified", "warning"),
        LeadStatus.CONVERTED: ("Converted", "success"),
        LeadStatus.LOST: ("Lost", "muted")
    }
    text, kind = badge_map.get(status, ("Unknown", "muted"))
    return ui_kit.badge(text, kind)


def _get_source_icon(source: LeadSource) -> str:
    """Get icon for lead source."""
    icons = {
        LeadSource.INSTAGRAM: "📷",
        LeadSource.FACEBOOK: "👥",
        LeadSource.WHATSAPP: "💬",
        LeadSource.REFERRAL: "🤝",
        LeadSource.OTHER: "📱"
    }
    return icons.get(source, "📱")


def _format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M")


def _init_mock_leads():
    """Initialize mock leads for demo."""
    if "leads_mock_initialized" in st.session_state:
        return
    
    leads_mgr = get_leads_manager()
    
    # Mock lead 1
    leads_mgr.create_lead(
        source=LeadSource.INSTAGRAM,
        name="Sarah Ahmed",
        phone="+971501234567",
        email="sarah.ahmed@example.com",
        tags=["hair-color", "appointment"],
        notes="Interested in hair coloring service"
    )
    
    # Mock lead 2
    leads_mgr.create_lead(
        source=LeadSource.WHATSAPP,
        name="Layla Hassan",
        phone="+971507654321",
        tags=["hair-treatment", "pricing"],
        notes="Asked about hair treatment prices"
    )
    
    # Mock lead 3
    leads_mgr.create_lead(
        source=LeadSource.FACEBOOK,
        name="Nour Khalil",
        phone="+971509876543",
        email="nour.khalil@example.com",
        tags=["makeup", "events"],
        notes="Event makeup inquiry"
    )
    
    # Update one lead to contacted status
    leads = leads_mgr.list_leads()
    if leads:
        leads_mgr.update_lead(leads[1].id, status=LeadStatus.CONTACTED)
    
    st.session_state.leads_mock_initialized = True
    logger.info("Initialized mock leads data")


def render_leads_view():
    """Render leads management view."""
    ui_kit.inject_ui_kit_css()
    
    # Initialize mock data
    _init_mock_leads()
    
    # Get leads manager
    leads_mgr = get_leads_manager()
    
    # Page header
    st.title("👥 Leads")
    st.caption("Manage customer leads and contacts")
    
    # Filters and actions
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "New", "Contacted", "Qualified", "Converted", "Lost"],
            key="leads_status_filter"
        )
    
    with col2:
        source_filter = st.selectbox(
            "Source",
            ["All", "Instagram", "Facebook", "WhatsApp", "Referral", "Other"],
            key="leads_source_filter"
        )
    
    with col3:
        search_query = st.text_input("Search", placeholder="Name, phone, email...", key="leads_search")
    
    with col4:
        st.write("")  # Spacing
        if st.button("🔄", use_container_width=True):
            st.rerun()
    
    st.divider()
    
    # Get leads
    status_enum = None if status_filter == "All" else LeadStatus[status_filter.upper()]
    source_enum = None if source_filter == "All" else LeadSource[source_filter.upper()]
    
    leads = leads_mgr.list_leads(status=status_enum, source=source_enum)
    
    # Apply search filter
    if search_query:
        search_lower = search_query.lower()
        leads = [
            l for l in leads
            if (l.name and search_lower in l.name.lower()) or
               (l.phone and search_lower in l.phone.lower()) or
               (l.email and search_lower in l.email.lower())
        ]
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        ui_kit.metric("Total Leads", str(len(leads_mgr.list_leads())))
    with col2:
        ui_kit.metric("New", str(len(leads_mgr.list_leads(status=LeadStatus.NEW))))
    with col3:
        ui_kit.metric("Qualified", str(len(leads_mgr.list_leads(status=LeadStatus.QUALIFIED))))
    with col4:
        ui_kit.metric("Converted", str(len(leads_mgr.list_leads(status=LeadStatus.CONVERTED))))
    
    st.divider()
    
    # Leads list
    if not leads:
        st.info("No leads found")
    else:
        ui_kit.section_title(f"Leads ({len(leads)})", "📋")
        
        # Display as cards
        for lead in leads:
            with ui_kit.card():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Lead name and source
                    st.markdown(f"### {_get_source_icon(lead.source)} {lead.name or 'Unknown'}")
                    
                    # Contact info
                    contact_parts = []
                    if lead.phone:
                        contact_parts.append(f"📞 {lead.phone}")
                    if lead.email:
                        contact_parts.append(f"✉️ {lead.email}")
                    
                    if contact_parts:
                        st.caption(" • ".join(contact_parts))
                    
                    # Tags
                    if lead.tags:
                        ui_kit.pills_row(lead.tags)
                    
                    # Notes
                    if lead.notes:
                        st.caption(f"📝 {lead.notes}")
                
                with col2:
                    # Status badge
                    st.markdown(_get_status_badge(lead.status), unsafe_allow_html=True)
                    
                    # Timestamps
                    st.caption(f"Created: {_format_datetime(lead.created_at)}")
                    if lead.last_interaction:
                        st.caption(f"Last: {_format_datetime(lead.last_interaction)}")
                    
                    # Actions
                    if st.button("View", key=f"view_lead_{lead.id}", use_container_width=True):
                        st.session_state.selected_lead_id = lead.id
                        st.session_state.show_lead_detail = True
                        st.rerun()
                
                st.divider()
    
    # Lead detail modal (if selected)
    if st.session_state.get("show_lead_detail"):
        selected_lead_id = st.session_state.get("selected_lead_id")
        lead = leads_mgr.get_lead(selected_lead_id) if selected_lead_id else None
        
        if lead:
            with st.expander("Lead Details", expanded=True):
                st.markdown(f"## {lead.name or 'Unknown Lead'}")
                
                # Edit form
                with st.form(key=f"edit_lead_{lead.id}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("Name", value=lead.name or "")
                        new_phone = st.text_input("Phone", value=lead.phone or "")
                        new_email = st.text_input("Email", value=lead.email or "")
                    
                    with col2:
                        new_status = st.selectbox(
                            "Status",
                            [s.value for s in LeadStatus],
                            index=[s.value for s in LeadStatus].index(lead.status.value)
                        )
                        new_source = st.selectbox(
                            "Source",
                            [s.value for s in LeadSource],
                            index=[s.value for s in LeadSource].index(lead.source.value)
                        )
                    
                    new_notes = st.text_area("Notes", value=lead.notes, height=100)
                    new_tags = st.text_input("Tags (comma-separated)", value=", ".join(lead.tags))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save", use_container_width=True):
                            # Update lead
                            leads_mgr.update_lead(
                                lead.id,
                                name=new_name,
                                phone=new_phone,
                                email=new_email,
                                status=LeadStatus(new_status),
                                source=LeadSource(new_source),
                                notes=new_notes,
                                tags=[t.strip() for t in new_tags.split(",") if t.strip()]
                            )
                            st.success("Lead updated!")
                            st.session_state.show_lead_detail = False
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state.show_lead_detail = False
                            st.rerun()


def leads_view():
    """Main entry point for leads view."""
    try:
        render_leads_view()
    except Exception as e:
        logger.error(f"Leads view error: {e}", exc_info=True)
        st.error(f"Error loading leads: {str(e)}")
