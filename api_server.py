"""
Simple API server for Lead Agent.
"""
import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

from lead_agent.orchestrator import LeadAgentOrchestrator
from lead_agent.llm.anthropic import AnthropicProvider
from lead_agent.config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Lead Agent
config = get_config()
llm_provider = AnthropicProvider(config["llm"]["anthropic"])
orchestrator = LeadAgentOrchestrator(llm_provider=llm_provider)

@app.route('/')
def home():
    return "Lead Agent API Server is running!"

@app.route('/api/analyze-product', methods=['POST'])
def analyze_product():
    """Analyze product and recommend target audience."""
    data = request.json
    product_description = data.get('description', '')
    
    if not product_description:
        return jsonify({'error': 'Product description is required'}), 400
    
    try:
        analysis = orchestrator.analyze_product(product_description)
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error analyzing product: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/find-leads', methods=['POST'])
def find_leads():
    """Find leads based on target audience."""
    data = request.json
    target_audience = data.get('target_audience', {})
    count = data.get('count', 10)
    
    if not target_audience:
        return jsonify({'error': 'Target audience is required'}), 400
    
    try:
        leads = orchestrator.find_leads(target_audience, count)
        return jsonify(leads)
    except Exception as e:
        logger.error(f"Error finding leads: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/personalize-messages', methods=['POST'])
def personalize_messages():
    """Personalize messages for leads."""
    data = request.json
    leads = data.get('leads', [])
    template = data.get('template', '')
    selected_ids = data.get('selected_ids', None)
    
    if not leads or not template:
        return jsonify({'error': 'Leads and template are required'}), 400
    
    try:
        messages = orchestrator.generate_personalized_sequences(leads, template, selected_ids)
        return jsonify(messages)
    except Exception as e:
        logger.error(f"Error personalizing messages: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-leads', methods=['POST'])
def save_leads():
    """Save leads to file."""
    data = request.json
    leads = data.get('leads', [])
    format = data.get('format', 'csv')
    
    if not leads:
        return jsonify({'error': 'Leads are required'}), 400
    
    try:
        path = orchestrator.save_leads(leads, format)
        return jsonify({'path': path})
    except Exception as e:
        logger.error(f"Error saving leads: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings."""
    try:
        return jsonify(config)
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings."""
    data = request.json
    
    try:
        # This is a simplified version - in a real app, you'd
        # update the actual config file or database
        # For now, we'll just return the data
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)