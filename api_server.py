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
        # Check if API key is configured
        if not config["llm"]["anthropic"]["api_key"]:
            # Return demo data if no API key is configured
            return jsonify({
                'target_audience': {
                    'title': 'Demo Target Audience',
                    'description': 'This is a demo response because the Anthropic API key is not configured.',
                    'industry': 'Technology',
                    'company_size': '10-500 employees',
                    'role': 'Decision Maker',
                    'pain_point': 'Efficiency'
                },
                'markets': [
                    {
                        'name': 'Software Companies',
                        'description': 'Companies that develop software products'
                    },
                    {
                        'name': 'Marketing Agencies',
                        'description': 'Agencies that provide marketing services'
                    }
                ],
                'outreach_strategies': [
                    {
                        'name': 'Email Outreach',
                        'description': 'Personalized email campaigns'
                    }
                ],
                'search_keywords': [
                    'AI script writing',
                    'automated content generation',
                    'script automation'
                ]
            })
        
        # Use only the LLM provider for product analysis to avoid scraper initialization
        analysis = llm_provider.analyze_product(product_description)
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
        # Check if Apify is enabled
        apify_enabled = config.get("scraping", {}).get("apify", {}).get("enabled", False)
        apify_api_key = config.get("scraping", {}).get("apify", {}).get("api_key", "")
        
        if apify_enabled and apify_api_key:
            logger.info("Using Apify integration for lead generation")
            # Use the orchestrator with the Apify scraper
            leads = orchestrator.find_leads(target_audience, count)
            return jsonify(leads)
        else:
            logger.warning("Apify not properly configured, using alternative method")
            # Use a more direct approach with just the search queries
            search_queries = llm_provider.generate_search_queries(target_audience)
            
            # Import the Apify scraper directly
            from lead_agent.scraper.apify_scraper import ApifyScraper
            scraper = ApifyScraper(config["scraping"])
            
            # Get leads directly from scraper
            leads = scraper.scrape_leads(search_queries, count)
            return jsonify(leads)
            
    except Exception as e:
        logger.error(f"Error finding leads: {str(e)}", exc_info=True)
        
        # Fallback to demo data if there's an error
        import uuid
        import random
        
        # List of demo companies and roles
        companies = ["TechFlow Solutions", "Nova Digital", "Spark Creative", "Quantum Industries", "DataWave Systems"]
        roles = ["CEO", "CTO", "Marketing Director", "Project Manager", "Operations Lead"]
        insights = [
            "Recently expanded their team",
            "Looking for new productivity tools",
            "Managing multiple client projects",
            "Facing workflow challenges",
            "Planning digital transformation"
        ]
        
        # Generate demo leads
        demo_leads = []
        for i in range(count):
            company = random.choice(companies)
            role = random.choice(roles)
            first_name = random.choice(["James", "Sarah", "Michael", "Emily", "David", "Jessica"])
            last_name = random.choice(["Smith", "Johnson", "Chen", "Rodriguez", "Taylor", "Kim"])
            
            industry = target_audience.get('industry', 'Technology')
            # Create personalized insight based on target audience
            personalized_insight = f"Working in the {industry} industry and {random.choice(insights).lower()} [DEMO FALLBACK]"
            
            lead = {
                "id": str(uuid.uuid4()),
                "name": f"{first_name} {last_name}",
                "company": company,
                "title": role,
                "email": f"{first_name.lower()}.{last_name.lower()}@{company.lower().replace(' ', '')}.com",
                "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "linkedin": f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{random.randint(10000, 99999)}",
                "source": "demo fallback",
                "insight": personalized_insight
            }
            demo_leads.append(lead)
        
        logger.info(f"Generated {len(demo_leads)} fallback demo leads")
        return jsonify(demo_leads)

@app.route('/api/test', methods=['GET'])
def test_api():
    """Test endpoint to verify API is working."""
    return jsonify({
        "status": "ok",
        "message": "API is working"
    })

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