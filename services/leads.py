"""
Lead management system with in-memory storage and DB stub.
Tracks potential customers and their interaction history.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LeadStatus(str, Enum):
    """Lead lifecycle status."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class LeadSource(str, Enum):
    """Lead acquisition channel."""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    WHATSAPP = "whatsapp"
    REFERRAL = "referral"
    OTHER = "other"


class Lead(BaseModel):
    """Lead/contact model."""
    id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    source: LeadSource
    status: LeadStatus = LeadStatus.NEW
    tags: List[str] = []
    notes: str = ""
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_interaction: Optional[datetime] = None


class LeadsManager:
    """
    Lead management with in-memory storage and future DB persistence.
    
    Responsibilities:
    - CRUD operations for leads
    - Lead status tracking
    - Integration with inbox (contact -> lead conversion)
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize leads manager.
        
        Args:
            db_manager: Optional DBManager instance for persistence (stub for now)
        """
        self.leads: Dict[str, Lead] = {}
        self.db = db_manager
        logger.info("LeadsManager initialized (in-memory mode)")
    
    def create_lead(
        self,
        source: LeadSource,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        **kwargs
    ) -> Lead:
        """
        Create new lead.
        
        Args:
            source: Lead source channel
            name: Contact name
            phone: Phone number
            email: Email address
            **kwargs: Additional metadata
            
        Returns:
            Created lead
        """
        # Generate ID (simple for now, can use UUID)
        lead_id = f"lead_{len(self.leads) + 1}_{int(datetime.now().timestamp())}"
        
        lead = Lead(
            id=lead_id,
            name=name,
            phone=phone,
            email=email,
            source=source,
            metadata=kwargs
        )
        
        self.leads[lead_id] = lead
        logger.info(f"Created lead: {lead_id}")
        
        # TODO: Persist to DB
        if self.db:
            pass  # self.db.save_lead(lead)
        
        return lead
    
    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Get lead by ID."""
        return self.leads.get(lead_id)
    
    def update_lead(self, lead_id: str, **updates) -> Optional[Lead]:
        """
        Update lead fields.
        
        Args:
            lead_id: Lead ID
            **updates: Fields to update
            
        Returns:
            Updated lead or None if not found
        """
        lead = self.leads.get(lead_id)
        if not lead:
            logger.warning(f"Lead not found: {lead_id}")
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        
        lead.updated_at = datetime.now()
        
        logger.info(f"Updated lead: {lead_id}")
        
        # TODO: Persist to DB
        if self.db:
            pass  # self.db.update_lead(lead)
        
        return lead
    
    def list_leads(
        self,
        status: Optional[LeadStatus] = None,
        source: Optional[LeadSource] = None,
        limit: int = 100
    ) -> List[Lead]:
        """
        List leads with optional filters.
        
        Args:
            status: Filter by status
            source: Filter by source
            limit: Maximum leads to return
            
        Returns:
            List of leads sorted by creation date (newest first)
        """
        leads = list(self.leads.values())
        
        # Apply filters
        if status:
            leads = [l for l in leads if l.status == status]
        if source:
            leads = [l for l in leads if l.source == source]
        
        # Sort by created_at, newest first
        leads.sort(key=lambda l: l.created_at, reverse=True)
        
        return leads[:limit]
    
    def update_interaction(self, lead_id: str) -> None:
        """Update last interaction timestamp."""
        lead = self.leads.get(lead_id)
        if lead:
            lead.last_interaction = datetime.now()
            lead.updated_at = datetime.now()
    
    def find_by_contact(self, phone: Optional[str] = None, email: Optional[str] = None) -> Optional[Lead]:
        """
        Find lead by contact info.
        
        Args:
            phone: Phone number
            email: Email address
            
        Returns:
            First matching lead or None
        """
        for lead in self.leads.values():
            if phone and lead.phone == phone:
                return lead
            if email and lead.email == email:
                return lead
        return None


# Global singleton
_leads_manager = None


def get_leads_manager() -> LeadsManager:
    """Get or create global leads manager instance."""
    global _leads_manager
    if _leads_manager is None:
        _leads_manager = LeadsManager()
    return _leads_manager
