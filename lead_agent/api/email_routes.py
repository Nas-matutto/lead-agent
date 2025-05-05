"""
API routes for email integration - simplified version.
"""
import os
import json
import logging
from flask import Blueprint, request, jsonify, redirect, session

from lead_agent.storage.email_db import EmailDB

logger = logging.getLogger(__name__)

# Create Blueprint
email_bp = Blueprint('email', __name__, url_prefix='/api/email')

# Initialize database
EmailDB.initialize_db()

# Simulated user ID (in a real app, this would come from authentication)
DEMO_USER_ID = "demo_user_123"

@email_bp.route('/status', methods=['GET'])
def get_email_status():
    """Get email connection status and settings."""
    # Check if user has a connection
    connection = EmailDB.get_connection(DEMO_USER_ID)
    connected = connection is not None
    
    # Get settings
    settings = EmailDB.get_settings(DEMO_USER_ID)
    
    # Format response
    response = {
        "connected": connected,
        "email": connection.get("email", "") if connected else "",
        "provider": connection.get("provider", "") if connected else "",
        "settings": {
            "sendTime": settings.get("send_time", "9"),
            "timezone": settings.get("timezone", "America/New_York"),
            "autoFollowup": settings.get("auto_followup", False),
            "followupDelay": settings.get("followup_delay", 3),
            "followupCount": settings.get("followup_count", 1)
        }
    }
    
    return jsonify(response)

@email_bp.route('/oauth/gmail', methods=['GET'])
def oauth_gmail():
    """Start Gmail OAuth flow."""
    # In a real app, this would redirect to Google OAuth
    # For now, simulate a successful connection
    return jsonify({
        "message": "This endpoint would redirect to Google OAuth. Simulate by using the SMTP option instead."
    })

@email_bp.route('/oauth/outlook', methods=['GET'])
def oauth_outlook():
    """Start Outlook OAuth flow."""
    # In a real app, this would redirect to Microsoft OAuth
    return jsonify({
        "message": "This endpoint would redirect to Microsoft OAuth. Simulate by using the SMTP option instead."
    })

@email_bp.route('/smtp', methods=['POST'])
def connect_smtp():
    """Connect with SMTP credentials."""
    data = request.json
    
    # Validate required fields
    required_fields = ['email', 'password', 'server', 'port']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Save connection
    EmailDB.save_connection(
        DEMO_USER_ID,
        data['email'],
        'smtp',
        {
            "smtp_server": data['server'],
            "smtp_port": data['port'],
            "smtp_username": data.get('username', data['email']),
            "smtp_password": data['password'],
            "smtp_use_ssl": data.get('use_ssl', False)
        }
    )
    
    return jsonify({
        "success": True,
        "email": data['email'],
        "provider": "smtp"
    })

@email_bp.route('/settings', methods=['GET'])
def get_email_settings():
    """Get email settings."""
    return get_email_status()

@email_bp.route('/settings', methods=['POST'])
def update_email_settings():
    """Update email settings."""
    data = request.json
    
    # Save settings
    EmailDB.save_settings(
        DEMO_USER_ID,
        {
            "send_time": data.get('sendTime', '9'),
            "timezone": data.get('timezone', 'America/New_York'),
            "auto_followup": data.get('autoFollowup', False),
            "followup_delay": data.get('followupDelay', 3),
            "followup_count": data.get('followupCount', 1)
        }
    )
    
    return jsonify({
        "success": True,
        "settings": data
    })

@email_bp.route('/disconnect', methods=['POST'])
def disconnect_email():
    """Disconnect email account."""
    # Remove connection
    if DEMO_USER_ID in EmailDB.email_connections:
        del EmailDB.email_connections[DEMO_USER_ID]
    
    return jsonify({
        "success": True
    })

@email_bp.route('/sequence', methods=['POST'])
def create_sequence():
    """Create and schedule an email sequence."""
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'leads', 'template', 'subject']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Check if user has an email connection
    if not EmailDB.get_connection(DEMO_USER_ID):
        return jsonify({"error": "No email connection found. Please connect an email account."}), 400
    
    # Create sequence
    sequence_id = EmailDB.create_sequence(DEMO_USER_ID, data['name'])
    
    return jsonify({
        "success": True,
        "sequence_id": sequence_id,
        "message": f"Sequence created with {len(data['leads'])} leads. In a real app, emails would be sent according to your schedule."
    })