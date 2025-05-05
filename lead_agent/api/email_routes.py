"""
API routes for email integration.
"""
import os
import json
import secrets
import logging
import requests
from urllib.parse import urlencode
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, redirect, session, url_for
from typing import Dict, Any

from lead_agent.storage.email_db import EmailDB
from lead_agent.services.email_service import EmailService
from lead_agent.config.oauth_config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GOOGLE_AUTH_URL, GOOGLE_TOKEN_URL, GOOGLE_SCOPE,
    MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_REDIRECT_URI, MICROSOFT_AUTH_URL, MICROSOFT_TOKEN_URL, MICROSOFT_SCOPE
)

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
    try:
        # Get connection
        connection = EmailDB.get_connection(DEMO_USER_ID)
        connected = connection is not None
        
        # Get settings
        settings = EmailDB.get_settings(DEMO_USER_ID)
        
        # Format response
        email_status = {
            "connected": connected,
            "email": connection['email'] if connected else "",
            "provider": connection['provider'] if connected else "",
            "settings": {
                "sendTime": settings['send_time'],
                "timezone": settings['timezone'],
                "autoFollowup": bool(settings['auto_followup']),
                "followupDelay": settings['followup_delay'],
                "followupCount": settings['followup_count']
            }
        }
        
        return jsonify(email_status)
        
    except Exception as e:
        logger.error(f"Error getting email status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@email_bp.route('/oauth/gmail', methods=['GET'])
def oauth_gmail():
    """Start Gmail OAuth flow."""
    try:
        # Generate state token to prevent CSRF
        state = secrets.token_urlsafe(16)
        session['oauth_state'] = state
        session['oauth_provider'] = 'gmail'
        
        # Build authorization URL
        auth_params = {
            'client_id': GOOGLE_CLIENT_ID,
            'redirect_uri': GOOGLE_REDIRECT_URI,
            'response_type': 'code',
            'scope': GOOGLE_SCOPE,
            'access_type': 'offline',
            'prompt': 'consent',
            'state': state
        }
        
        auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(auth_params)}"
        
        # Redirect to authorization URL
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"Error starting Gmail OAuth: {str(e)}")
        return jsonify({"error": str(e)}), 500

@email_bp.route('/oauth/outlook', methods=['GET'])
def oauth_outlook():
    """Start Outlook OAuth flow."""
    try:
        # Generate state token to prevent CSRF
        state = secrets.token_urlsafe(16)
        session['oauth_state'] = state
        session['oauth_provider'] = 'outlook'
        
        # Build authorization URL
        auth_params = {
            'client_id': MICROSOFT_CLIENT_ID,
            'redirect_uri': MICROSOFT_REDIRECT_URI,
            'response_type': 'code',
            'scope': MICROSOFT_SCOPE,
            'response_mode': 'query',
            'state': state
        }
        
        auth_url = f"{MICROSOFT_AUTH_URL}?{urlencode(auth_params)}"
        
        # Redirect to authorization URL
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"Error starting Outlook OAuth: {str(e)}")
        return jsonify({"error": str(e)}), 500

@email_bp.route('/oauth/callback', methods=['GET'])
def oauth_callback():
    """Handle OAuth callback."""
    try:
        # Get authorization code and state
        code = request.args.get('code')
        state = request.args.get('state')
        
        # Verify state token to prevent CSRF
        if state != session.get('oauth_state'):
            return jsonify({"error": "Invalid state parameter"}), 400
        
        # Get provider
        provider = session.get('oauth_provider')
        
        if provider == 'gmail':
            # Exchange code for tokens
            token_params = {
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'code': code,
                'redirect_uri': GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
            
            response = requests.post(GOOGLE_TOKEN_URL, data=token_params)
            tokens = response.json()
            
            if 'error' in tokens:
                return jsonify({"error": tokens['error']}), 400
            
            # Get user info
            user_info_response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f"Bearer {tokens['access_token']}"}
            )
            user_info = user_info_response.json()
            
            # Save connection
            EmailDB.save_connection(
                DEMO_USER_ID,
                user_info['email'],
                'gmail',
                {
                    'access_token': tokens['access_token'],
                    'refresh_token': tokens.get('refresh_token', '')
                }
            )
            
            # Redirect to frontend with success message
            return redirect(f"/settings?connected=true&email={user_info['email']}&provider=gmail")
            
        elif provider == 'outlook':
            # Exchange code for tokens
            token_params = {
                'client_id': MICROSOFT_CLIENT_ID,
                'client_secret': MICROSOFT_CLIENT_SECRET,
                'code': code,
                'redirect_uri': MICROSOFT_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
            
            response = requests.post(MICROSOFT_TOKEN_URL, data=token_params)
            tokens = response.json()
            
            if 'error' in tokens:
                return jsonify({"error": tokens['error']}), 400
            
            # Get user info
            user_info_response = requests.get(
                'https://graph.microsoft.com/v1.0/me',
                headers={'Authorization': f"Bearer {tokens['access_token']}"}
            )
            user_info = user_info_response.json()
            
            # Save connection
            EmailDB.save_connection(
                DEMO_USER_ID,
                user_info['mail'],
                'outlook',
                {
                    'access_token': tokens['access_token'],
                    'refresh_token': tokens.get('refresh_token', '')
                }
            )
            
            # Redirect to frontend with success message
            return redirect(f"/settings?connected=true&email={user_info['mail']}&provider=outlook")
        
        else:
            return jsonify({"error": "Invalid OAuth provider"}), 400
            
    except Exception as e:
        logger.error(f"Error handling OAuth callback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@email_bp.route('/smtp', methods=['POST'])
def connect_smtp():
    """Connect with SMTP credentials."""
    try:
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
                'server': data['server'],
                'port': data['port'],
                'username': data.get('username', data['email']),
                'password': data['password'],
                'use_ssl': data.get('use_ssl', False)
            }
        )
        
        return jsonify({
            "success": True,
            "email": data['email'],
            "provider": "smtp"
        })
        
    except Exception as e:
        logger.error(f"Error connecting SMTP: {str(e)}")
        return jsonify({"error": str(e)}), 500

@email_bp.route('/settings', methods=['GET'])
def get_email_settings():
    """Get email settings."""
    try:
        # Get connection
        connection = EmailDB.get_connection(DEMO_USER_ID)
        connected = connection is not None
        
        # Get settings
        settings = EmailDB.get_settings(DEMO_USER_ID)
        
        # Format response
        email_settings = {
            "connected": connected,
            "email": connection['email'] if connected else "",
            "provider": connection['provider'] if connected else "",
            "settings": {
                "sendTime": settings['send_time'],
                "timezone": settings['timezone'],
                "autoFollowup": bool(settings['auto_followup']),
                "followupDelay": settings['followup_delay'],
                "followupCount": settings['followup_count']
            }
        }
        
        return jsonify(email_settings)
        
    except Exception as e:
        logger.error(f"Error getting email settings: {str(e)}")
        return jsonify({"error": str(e)}), 500

@email_bp.route('/settings', methods=['POST'])
def update_email_settings():
    """Update email settings."""
    try:
        data = request.json
        
        # Save settings
        EmailDB.save_settings(
            DEMO_USER_ID,
            {
                'send_time': data.get('sendTime', '9'),
                'timezone': data.get('timezone', 'America/New_York'),
                'auto_followup': data.get('autoFollowup', False),
                'followup_delay': data.get('followupDelay', 3),
                'followup_count': data.get('followupCount', 1)
            }
        )
        
        return jsonify({
            "success": True,
            "settings": data
        })
        
    except Exception as e:
        logger.error(f"Error updating email settings: {str(e)}")
        return jsonify({"error": str(e)}), 500

@email_bp.route('/disconnect', methods=['POST'])
def disconnect_email():
    """Disconnect email account."""
    try:
        # Delete connection
        conn = EmailDB.connect()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM email_connections WHERE user_id = ?", (DEMO_USER_ID,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error disconnecting email: {str(e)}")
        return jsonify({"error": str(e)}), 500

@email_bp.route('/sequence', methods=['POST'])
def create_sequence():
    """Create and schedule an email sequence."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'leads', 'template', 'subject']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if user has an email connection
        connection = EmailDB.get_connection(DEMO_USER_ID)
        if not connection:
            return jsonify({"error": "No email connection found. Please connect an email account."}), 400
        
        # Create sequence
        sequence_id = EmailService.create_sequence(
            DEMO_USER_ID,
            data['name'],
            data['leads'],
            data['template'],
            data['subject']
        )
        
        if sequence_id < 0:
            return jsonify({"error": "Failed to create sequence"}), 500
        
        return jsonify({
            "success": True,
            "sequence_id": sequence_id
        })
        
    except Exception as e:
        logger.error(f"Error creating sequence: {str(e)}")
        return jsonify({"error": str(e)}), 500

@email_bp.route('/test', methods=['POST'])
def test_email():
    """Send a test email."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['to_email', 'subject', 'body']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if user has an email connection
        connection = EmailDB.get_connection(DEMO_USER_ID)
        if not connection:
            return jsonify({"error": "No email connection found. Please connect an email account."}), 400
        
        # Send test email
        success = EmailService.send_email(
            DEMO_USER_ID,
            data['to_email'],
            data['subject'],
            data['body']
        )
        
        if not success:
            return jsonify({"error": "Failed to send test email"}), 500
        
        return jsonify({
            "success": True,
            "message": f"Test email sent to {data['to_email']}"
        })
        
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        return jsonify({"error": str(e)}), 500