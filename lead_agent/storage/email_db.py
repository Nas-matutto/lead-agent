"""
Database models for email integration.
"""
import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DB_PATH = os.path.join("data", "email.db")

def initialize_db():
    """Create the necessary tables if they don't exist."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Email connections table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS email_connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        email TEXT NOT NULL,
        provider TEXT NOT NULL,
        oauth_token TEXT,
        oauth_refresh_token TEXT,
        smtp_server TEXT,
        smtp_port INTEGER,
        smtp_username TEXT,
        smtp_password TEXT,
        smtp_use_ssl BOOLEAN,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Email settings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS email_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        send_time TEXT DEFAULT '9',
        timezone TEXT DEFAULT 'America/New_York',
        auto_followup BOOLEAN DEFAULT 0,
        followup_delay INTEGER DEFAULT 3,
        followup_count INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Email sequences table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS email_sequences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        status TEXT DEFAULT 'draft',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Sequence recipients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sequence_recipients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sequence_id INTEGER NOT NULL,
        lead_id TEXT NOT NULL,
        lead_data TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sequence_id) REFERENCES email_sequences (id)
    )
    ''')
    
    # Email messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS email_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sequence_id INTEGER NOT NULL,
        recipient_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        body TEXT NOT NULL,
        step INTEGER DEFAULT 0,
        scheduled_at TIMESTAMP,
        sent_at TIMESTAMP,
        status TEXT DEFAULT 'scheduled',
        tracking_id TEXT,
        opened BOOLEAN DEFAULT 0,
        replied BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sequence_id) REFERENCES email_sequences (id),
        FOREIGN KEY (recipient_id) REFERENCES sequence_recipients (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    logger.info("Email database initialized")

class EmailDB:
    """Database operations for email integration."""
    
    @staticmethod
    def connect():
        """Connect to the database."""
        return sqlite3.connect(DB_PATH)
    
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
        conn = EmailDB.connect()
        cursor = conn.cursor()
        
        # Delete any existing connection for this user
        cursor.execute("DELETE FROM email_connections WHERE user_id = ?", (user_id,))
        
        if provider == "gmail" or provider == "outlook":
            # OAuth credentials
            cursor.execute(
                """
                INSERT INTO email_connections 
                (user_id, email, provider, oauth_token, oauth_refresh_token)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    email,
                    provider,
                    credentials.get("access_token", ""),
                    credentials.get("refresh_token", "")
                )
            )
        else:
            # SMTP credentials
            cursor.execute(
                """
                INSERT INTO email_connections 
                (user_id, email, provider, smtp_server, smtp_port, smtp_username, smtp_password, smtp_use_ssl)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    email,
                    provider,
                    credentials.get("server", ""),
                    credentials.get("port", 587),
                    credentials.get("username", email),
                    credentials.get("password", ""),
                    credentials.get("use_ssl", False)
                )
            )
        
        connection_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return connection_id
    
    @staticmethod
    def get_connection(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get email connection information for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Connection information or None if not found
        """
        conn = EmailDB.connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM email_connections WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        
        return None
    
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
        conn = EmailDB.connect()
        cursor = conn.cursor()
        
        # Check if settings already exist
        cursor.execute("SELECT id FROM email_settings WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            # Update existing settings
            cursor.execute(
                """
                UPDATE email_settings 
                SET send_time = ?, timezone = ?, auto_followup = ?, followup_delay = ?, followup_count = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """,
                (
                    settings.get("send_time", "9"),
                    settings.get("timezone", "America/New_York"),
                    1 if settings.get("auto_followup", False) else 0,
                    settings.get("followup_delay", 3),
                    settings.get("followup_count", 1),
                    user_id
                )
            )
            settings_id = row[0]
        else:
            # Insert new settings
            cursor.execute(
                """
                INSERT INTO email_settings 
                (user_id, send_time, timezone, auto_followup, followup_delay, followup_count)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    settings.get("send_time", "9"),
                    settings.get("timezone", "America/New_York"),
                    1 if settings.get("auto_followup", False) else 0,
                    settings.get("followup_delay", 3),
                    settings.get("followup_count", 1)
                )
            )
            settings_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return settings_id
    
    @staticmethod
    def get_settings(user_id: str) -> Dict[str, Any]:
        """
        Get email settings for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Email settings
        """
        conn = EmailDB.connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM email_settings WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        
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
        conn = EmailDB.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO email_sequences
            (user_id, name)
            VALUES (?, ?)
            """,
            (user_id, name)
        )
        
        sequence_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return sequence_id
    
    @staticmethod
    def add_recipient(sequence_id: int, lead_id: str, lead_data: Dict[str, Any]) -> int:
        """
        Add a recipient to a sequence.
        
        Args:
            sequence_id: Sequence ID
            lead_id: Lead ID
            lead_data: Lead data
            
        Returns:
            Recipient ID
        """
        conn = EmailDB.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO sequence_recipients
            (sequence_id, lead_id, lead_data)
            VALUES (?, ?, ?)
            """,
            (sequence_id, lead_id, json.dumps(lead_data))
        )
        
        recipient_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return recipient_id
    
    @staticmethod
    def schedule_email(sequence_id: int, recipient_id: int, subject: str, body: str, step: int, scheduled_at: str) -> int:
        """
        Schedule an email.
        
        Args:
            sequence_id: Sequence ID
            recipient_id: Recipient ID
            subject: Email subject
            body: Email body
            step: Sequence step (0 = initial, 1+ = follow-up)
            scheduled_at: Scheduled send time
            
        Returns:
            Email ID
        """
        conn = EmailDB.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO email_messages
            (sequence_id, recipient_id, subject, body, step, scheduled_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (sequence_id, recipient_id, subject, body, step, scheduled_at)
        )
        
        email_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return email_id