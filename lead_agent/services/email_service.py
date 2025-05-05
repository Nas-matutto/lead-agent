"""
Email service for sending emails through various providers.
"""
import os
import json
import logging
import uuid
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from lead_agent.storage.email_db import EmailDB

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails and managing sequences."""
    
    def __init__(self):
        """Initialize the email service."""
        pass
    
    @staticmethod
    def format_email_body(template: str, lead: Dict[str, Any]) -> str:
        """
        Format an email template with lead data.
        
        Args:
            template: Email template with placeholders
            lead: Lead data
            
        Returns:
            Formatted email body
        """
        body = template
        
        # Replace placeholders
        for key, value in lead.items():
            placeholder = f"{{{key}}}"
            if placeholder in body:
                body = body.replace(placeholder, str(value))
        
        return body
    
    @staticmethod
    def send_email(user_id: str, to_email: str, subject: str, body: str) -> bool:
        """
        Send an email using the user's connected account.
        
        Args:
            user_id: User ID
            to_email: Recipient email
            subject: Email subject
            body: Email body
            
        Returns:
            True if email was sent successfully
        """
        try:
            # Get user's email connection
            connection = EmailDB.get_connection(user_id)
            if not connection:
                logger.error(f"No email connection found for user {user_id}")
                return False
            
            provider = connection['provider']
            
            if provider == "gmail":
                return EmailService._send_via_gmail(connection, to_email, subject, body)
            elif provider == "outlook":
                return EmailService._send_via_outlook(connection, to_email, subject, body)
            else:
                return EmailService._send_via_smtp(connection, to_email, subject, body)
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    @staticmethod
    def _send_via_gmail(connection: Dict[str, Any], to_email: str, subject: str, body: str) -> bool:
        """Send email via Gmail API."""
        try:
            # In a production app, you would use the Google API client library
            # For this example, we'll simulate success
            logger.info(f"Sending email via Gmail from {connection['email']} to {to_email}")
            
            # Simulate API call
            # In a real implementation, you would:
            # 1. Use the oauth_token to authenticate with the Gmail API
            # 2. Create and send the email using the API
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending via Gmail: {str(e)}")
            return False
    
    @staticmethod
    def _send_via_outlook(connection: Dict[str, Any], to_email: str, subject: str, body: str) -> bool:
        """Send email via Outlook API."""
        try:
            # In a production app, you would use the Microsoft Graph API
            # For this example, we'll simulate success
            logger.info(f"Sending email via Outlook from {connection['email']} to {to_email}")
            
            # Simulate API call
            # In a real implementation, you would:
            # 1. Use the oauth_token to authenticate with the Microsoft Graph API
            # 2. Create and send the email using the API
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending via Outlook: {str(e)}")
            return False
    
    @staticmethod
    def _send_via_smtp(connection: Dict[str, Any], to_email: str, subject: str, body: str) -> bool:
        """Send email via SMTP."""
        try:
            # Get SMTP settings
            smtp_server = connection['smtp_server']
            smtp_port = int(connection['smtp_port'])
            smtp_username = connection['smtp_username'] or connection['email']
            smtp_password = connection['smtp_password']
            use_ssl = bool(connection['smtp_use_ssl'])
            from_email = connection['email']
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to SMTP server
            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            else:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
            
            # Login and send
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Sent email via SMTP from {from_email} to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending via SMTP: {str(e)}")
            return False
    
    @staticmethod
    def create_sequence(user_id: str, name: str, leads: List[Dict[str, Any]], template: str, subject: str) -> int:
        """
        Create and schedule an email sequence.
        
        Args:
            user_id: User ID
            name: Sequence name
            leads: List of leads
            template: Email template
            subject: Email subject
            
        Returns:
            Sequence ID
        """
        try:
            # Create sequence
            sequence_id = EmailDB.create_sequence(user_id, name)
            
            # Get user settings
            settings = EmailDB.get_settings(user_id)
            
            # Calculate send time
            send_hour = int(settings['send_time'])
            now = datetime.now()
            
            # Schedule for next business day at the specified hour
            days_to_add = 1
            if now.weekday() >= 4:  # Friday, Saturday
                days_to_add = 7 - now.weekday()  # Schedule for Monday
                
            scheduled_date = now + timedelta(days=days_to_add)
            scheduled_at = scheduled_date.replace(hour=send_hour, minute=0, second=0, microsecond=0)
            
            # Add recipients and schedule emails
            for lead in leads:
                # Add recipient
                recipient_id = EmailDB.add_recipient(sequence_id, lead['id'], lead)
                
                # Format body
                body = EmailService.format_email_body(template, lead)
                
                # Schedule initial email
                EmailDB.schedule_email(
                    sequence_id,
                    recipient_id,
                    subject,
                    body,
                    0,  # Initial email
                    scheduled_at.isoformat()
                )
                
                # Schedule follow-ups if enabled
                if settings['auto_followup']:
                    followup_delay = int(settings['followup_delay'])
                    followup_count = int(settings['followup_count'])
                    
                    for step in range(1, followup_count + 1):
                        # Calculate follow-up date
                        followup_date = scheduled_date + timedelta(days=followup_delay * step)
                        
                        # Skip weekends
                        while followup_date.weekday() >= 5:  # Saturday or Sunday
                            followup_date = followup_date + timedelta(days=1)
                        
                        followup_at = followup_date.replace(hour=send_hour, minute=0, second=0, microsecond=0)
                        
                        # Format follow-up body
                        followup_template = f"""
                        I wanted to follow-up on my previous message regarding {lead.get('company', 'your company')}.
                        
                        {template}
                        """
                        followup_body = EmailService.format_email_body(followup_template, lead)
                        
                        # Schedule follow-up
                        EmailDB.schedule_email(
                            sequence_id,
                            recipient_id,
                            f"Follow-up: {subject}",
                            followup_body,
                            step,
                            followup_at.isoformat()
                        )
            
            logger.info(f"Created sequence {sequence_id} with {len(leads)} recipients")
            return sequence_id
            
        except Exception as e:
            logger.error(f"Error creating sequence: {str(e)}")
            return -1
    
    @staticmethod
    def process_pending_emails():
        """Process pending emails that are due to be sent."""
        conn = EmailDB.connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        # Get emails that are scheduled to be sent
        cursor.execute(
            """
            SELECT e.*, r.lead_id, r.lead_data, s.user_id
            FROM email_messages e
            JOIN sequence_recipients r ON e.recipient_id = r.id
            JOIN email_sequences s ON e.sequence_id = s.id
            WHERE e.status = 'scheduled' AND e.scheduled_at <= ?
            """,
            (now,)
        )
        
        emails = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Send emails
        for email in emails:
            lead_data = json.loads(email['lead_data'])
            user_id = email['user_id']
            to_email = lead_data.get('email', '')
            
            if to_email:
                success = EmailService.send_email(
                    user_id,
                    to_email,
                    email['subject'],
                    email['body']
                )
                
                # Update email status
                conn = EmailDB.connect()
                cursor = conn.cursor()
                
                if success:
                    # Generate tracking ID
                    tracking_id = str(uuid.uuid4())
                    
                    cursor.execute(
                        """
                        UPDATE email_messages
                        SET status = 'sent', sent_at = CURRENT_TIMESTAMP, tracking_id = ?
                        WHERE id = ?
                        """,
                        (tracking_id, email['id'])
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE email_messages
                        SET status = 'failed'
                        WHERE id = ?
                        """,
                        (email['id'],)
                    )
                
                conn.commit()
                conn.close()