"""
Data processing and cleaning module for Lead Agent.
"""
import logging
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DataProcessor:
    """Processor for cleaning and validating lead data."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the data processor.
        
        Args:
            config: Processor configuration
        """
        self.config = config
    
    def _clean_email(self, email: str) -> str:
        """
        Clean and validate an email address.
        
        Args:
            email: Email address
            
        Returns:
            Cleaned email or empty string if invalid
        """
        if not email:
            return ""
            
        # Basic email validation
        email = email.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return ""
            
        return email
    
    def _clean_phone(self, phone: str) -> str:
        """
        Clean and validate a phone number.
        
        Args:
            phone: Phone number
            
        Returns:
            Cleaned phone number or empty string if invalid
        """
        if not phone:
            return ""
            
        # Remove non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Basic validation (at least 7 digits)
        if len(digits) < 7:
            return ""
            
        # Format phone number (simplified)
        if len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        else:
            return digits
    
    def _clean_name(self, name: str) -> str:
        """
        Clean and validate a name.
        
        Args:
            name: Name
            
        Returns:
            Cleaned name or empty string if invalid
        """
        if not name:
            return ""
            
        # Basic cleaning
        name = name.strip()
        
        # Remove titles and extras
        name = re.sub(r'^(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+', '', name)
        
        # Limit length
        if len(name) > 100:
            return ""
            
        return name
    
    def process_leads(
        self, 
        leads: List[Dict[str, Any]], 
        target_audience: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process and clean lead data.
        
        Args:
            leads: List of lead dictionaries
            target_audience: Target audience profile (optional)
            
        Returns:
            List of processed lead dictionaries
        """
        processed_leads = []
        
        for lead in leads:
            # Clean basic fields
            processed_lead = {
                "id": lead.get("id", ""),
                "name": self._clean_name(lead.get("name", "")),
                "email": self._clean_email(lead.get("email", "")),
                "phone": self._clean_phone(lead.get("phone", "")),
                "company": lead.get("company", "").strip(),
                "title": lead.get("title", "").strip(),
                "linkedin": lead.get("linkedin", "").strip(),
                "website": lead.get("website", "").strip(),
                "source": lead.get("source", "").strip()
            }
            
            # Only keep leads with at least email or phone
            if processed_lead["email"] or processed_lead["phone"]:
                processed_leads.append(processed_lead)
        
        logger.info(f"Processed {len(processed_leads)} leads")
        return processed_leads