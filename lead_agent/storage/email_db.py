"""
Simplified email database module for Lead Agent.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# In-memory storage for demo purposes
email_connections = {}
email_settings = {}
email_sequences = {}

class EmailDB:
    """Simple in-memory database for email integration."""
    
    @staticmethod
    def initialize_db():
        """Initialize the database."""
        logger.info("Email database initialized (in-memory version)")
    
    @staticmethod
    def save_connection(user_id: str, email: str, provider: str, credentials: Dict[str, Any]) -> int:
        """
        Save email connection information.
        
        Args:
            user_id: User ID
            email: Email address
            provider: Email provider (gmail, outlook, smtp)
            credentials: Provider-specific credentials
            
        Returns:
            Connection ID
        """
        connection = {
            "id": len(email_connections) + 1,
            "email": email,
            "provider": provider,
            **credentials
        }
        
        email_connections[user_id] = connection
        
        return connection["id"]
    
    @staticmethod
    def get_connection(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get email connection information for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Connection information or None if not found
        """
        return email_connections.get(user_id)
    
    @staticmethod
    def save_settings(user_id: str, settings: Dict[str, Any]) -> int:
        """
        Save email settings for a user.
        
        Args:
            user_id: User ID
            settings: Email settings
            
        Returns:
            Settings ID
        """
        email_settings[user_id] = {
            "id": len(email_settings) + 1,
            **settings
        }
        
        return email_settings[user_id]["id"]
    
    @staticmethod
    def get_settings(user_id: str) -> Dict[str, Any]:
        """
        Get email settings for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Email settings
        """
        if user_id in email_settings:
            return email_settings[user_id]
        
        # Return default settings
        return {
            "send_time": "9",
            "timezone": "America/New_York",
            "auto_followup": False,
            "followup_delay": 3,
            "followup_count": 1
        }
    
    @staticmethod
    def create_sequence(user_id: str, name: str) -> int:
        """
        Create a new email sequence.
        
        Args:
            user_id: User ID
            name: Sequence name
            
        Returns:
            Sequence ID
        """
        sequence_id = len(email_sequences) + 1
        
        email_sequences[sequence_id] = {
            "id": sequence_id,
            "user_id": user_id,
            "name": name,
            "status": "draft",
            "recipients": []
        }
        
        return sequence_id
    