"""
Simple API server for Lead Agent with email integration.
"""
import os
import json
import logging
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS

from lead_agent.orchestrator import LeadAgentOrchestrator
from lead_agent.llm.anthropic import AnthropicProvider
from lead_agent.config import get_config
from lead_agent.api.email_routes import email_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='frontend')
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))  # Required for sessions
CORS(app)  # Enable CORS for all routes

# Initialize Lead Agent
config = get_config()
llm_provider = AnthropicProvider(config["llm"]["anthropic"])
orchestrator = LeadAgentOrchestrator(llm_provider=llm_provider)

# Register blueprints
app.register_blueprint(email_bp)

# Serve frontend files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)