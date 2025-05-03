"""
Test the complete lead generation workflow.
"""
import logging
from lead_agent.orchestrator import LeadAgentOrchestrator
from lead_agent.llm.anthropic import AnthropicProvider
from lead_agent.config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run the test workflow."""
    # Get configuration
    config = get_config()
    
    # Create LLM provider with actual API key
    llm_provider = AnthropicProvider(config["llm"]["anthropic"])
    
    # Create orchestrator
    orchestrator = LeadAgentOrchestrator(llm_provider=llm_provider)
    
    # Test product analysis
    product_description = "We sell a cloud-based project management software that helps teams track tasks, collaborate on documents, and automate workflows. It integrates with popular tools like Slack, Google Workspace, and Microsoft Office."
    
    print("\n===== ANALYZING PRODUCT =====")
    analysis = orchestrator.analyze_product(product_description)
    
    print(f"\nTarget Audience: {analysis['target_audience']['title']}")
    print(f"Description: {analysis['target_audience']['description']}")
    
    print("\nRecommended Markets:")
    for market in analysis['markets']:
        print(f"- {market['name']}: {market['description']}")
    
    print("\nSearch Keywords:")
    for keyword in analysis['search_keywords']:
        print(f"- {keyword}")
    
    # Test lead generation (limit to 2 for testing)
    print("\n===== FINDING LEADS =====")
    leads = orchestrator.find_leads(analysis['target_audience'], count=2)
    
    print(f"\nFound {len(leads)} leads:")
    for lead in leads:
        print(f"\n- {lead.get('name', 'No name')} ({lead.get('company', 'Unknown company')})")
        print(f"  Email: {lead.get('email', 'No email')}")
        print(f"  Phone: {lead.get('phone', 'No phone')}")
        print(f"  Website: {lead.get('website', 'No website')}")
    
    # Save leads to file
    print("\n===== SAVING LEADS =====")
    output_path = orchestrator.save_leads(leads)
    print(f"Saved leads to {output_path}")
    
    # Test message personalization
    print("\n===== PERSONALIZING MESSAGES =====")
    template = "Hi {name}, I noticed {company} is {insight}. I'd love to show you how our product can help with your project management needs."
    
    messages = orchestrator.generate_personalized_sequences(leads, template)
    
    print("\nPersonalized messages:")
    for lead_id, message in messages.items():
        lead = next((l for l in leads if str(l.get("id")) == str(lead_id)), None)
        if lead:
            print(f"\nTo: {lead.get('name', 'No name')} ({lead.get('company', 'Unknown company')})")
            print(f"Message: {message}")

if __name__ == "__main__":
    main()