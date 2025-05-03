"""
Message personalization module for Lead Agent.
"""
import logging
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MessagePersonalizer:
    """Personalizer for outreach messages."""
    
    def __init__(self, llm_provider):
        """
        Initialize the message personalizer.
        
        Args:
            llm_provider: LLM provider for generating personalized content
        """
        self.llm_provider = llm_provider
    
    def personalize(
        self, 
        leads: List[Dict[str, Any]], 
        template: str, 
        selected_ids: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate personalized messages for leads.
        
        Args:
            leads: List of lead dictionaries
            template: Message template
            selected_ids: IDs of selected leads (if None, use all)
            
        Returns:
            Dictionary mapping lead IDs to personalized content
        """
        # Filter leads if IDs are provided
        if selected_ids:
            filtered_leads = [lead for lead in leads if str(lead.get("id")) in [str(id) for id in selected_ids]]
        else:
            filtered_leads = leads
            
        logger.info(f"Personalizing messages for {len(filtered_leads)} leads")
        
        # Enrich leads with insights if not already present
        if filtered_leads and "insight" not in filtered_leads[0]:
            # Create placeholder target audience for enrichment
            target_audience = {
                "title": "Target Audience",
                "description": "Businesses that could benefit from our product"
            }
            enriched_leads = self.llm_provider.enrich_leads(filtered_leads, target_audience)
        else:
            enriched_leads = filtered_leads
            
        # Use LLM to generate personalized messages
        messages = self.llm_provider.personalize_messages(enriched_leads, template)
        
        # Format results with additional metadata
        results = {}
        for lead_id, message in messages.items():
            lead = next((l for l in enriched_leads if str(l.get("id")) == str(lead_id)), None)
            if lead:
                results[lead_id] = {
                    "subject": f"Introduction from [Your Company] to {lead.get('company', 'Your Company')}",
                    "message": message,
                    "lead": lead
                }
                
        return results
    
    def generate_follow_up(
        self, 
        lead: Dict[str, Any], 
        previous_message: str, 
        days_since_sent: int = 7
    ) -> Dict[str, str]:
        """
        Generate a follow-up message.
        
        Args:
            lead: Lead dictionary
            previous_message: Previous message sent
            days_since_sent: Days since previous message was sent
            
        Returns:
            Dictionary with subject and message
        """
        # Use LLM to generate follow-up message
        subject_prefix = "Re: "
        if previous_message.startswith("Subject:"):
            subject_line = previous_message.split("\n")[0]
            subject = subject_prefix + subject_line[9:].strip()
        else:
            subject = subject_prefix + f"Introduction to {lead.get('company', 'Your Company')}"
            
        # Create a system prompt for the LLM
        system_prompt = "You are an expert in sales follow-up messages. Your task is to create an effective, friendly follow-up email that references the original message but adds new value."
        
        user_prompt = f"""
        Generate a follow-up message for this lead:
        
        LEAD INFO:
        Name: {lead.get('name', 'Prospect')}
        Company: {lead.get('company', 'Company')}
        Title: {lead.get('title', '')}
        
        ORIGINAL MESSAGE SENT {days_since_sent} DAYS AGO:
        {previous_message}
        
        Create a brief, friendly follow-up that:
        1. References the original message
        2. Adds a new insight or value proposition
        3. Includes a clear but gentle call to action
        4. Is no more than 4-5 sentences
        
        Just provide the message body, no need for subject line or formatting.
        """
        
        # Placeholder for actual LLM call
        follow_up_message = self.llm_provider._call_model(system_prompt, user_prompt)
        
        return {
            "subject": subject,
            "message": follow_up_message
        }