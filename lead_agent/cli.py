"""
Command Line Interface for Lead Agent.
"""
import os
import sys
import logging
import click
import pandas as pd
from typing import List, Dict, Any, Optional

from lead_agent.orchestrator import LeadAgentOrchestrator
from lead_agent.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create orchestrator instance
orchestrator = LeadAgentOrchestrator()

@click.group()
def cli():
    """Lead Agent - B2B Lead Generation Tool."""
    pass

@cli.command("analyze")
@click.option("--product", "-p", prompt="What product or service are you selling?",
              help="Description of your product or service")
def analyze_product(product: str):
    """Analyze a product and recommend target audience."""
    click.echo(f"Analyzing product: {product}")
    
    # Get product analysis from the orchestrator
    analysis = orchestrator.analyze_product(product)
    
    # Display the analysis
    click.echo("\n✅ Product Analysis Complete")
    click.echo("=" * 50)
    click.echo(f"📊 Target Audience: {analysis['target_audience']['title']}")
    click.echo(f"🔍 Description: {analysis['target_audience']['description']}")
    click.echo("\n🌍 Recommended Markets:")
    for market in analysis['markets']:
        click.echo(f"  • {market['name']}: {market['description']}")
    
    click.echo("\n📣 Outreach Strategies:")
    for strategy in analysis['outreach_strategies']:
        click.echo(f"  • {strategy['name']}: {strategy['description']}")
    
    click.echo("\n🔎 Search Keywords:")
    for keyword in analysis['search_keywords']:
        click.echo(f"  • {keyword}")
    
    # Save analysis for future use
    if not os.path.exists("data"):
        os.makedirs("data")
    
    with open("data/latest_analysis.txt", "w") as f:
        f.write(f"Product: {product}\n\n")
        f.write(f"Target Audience: {analysis['target_audience']['title']}\n")
        f.write(f"Description: {analysis['target_audience']['description']}\n\n")
        f.write("Recommended Markets:\n")
        for market in analysis['markets']:
            f.write(f"- {market['name']}: {market['description']}\n")
        f.write("\nOutreach Strategies:\n")
        for strategy in analysis['outreach_strategies']:
            f.write(f"- {strategy['name']}: {strategy['description']}\n")
        f.write("\nSearch Keywords:\n")
        for keyword in analysis['search_keywords']:
            f.write(f"- {keyword}\n")
    
    click.echo(f"\nAnalysis saved to data/latest_analysis.txt")
    click.echo("\nRun 'lead-agent find-leads' to find leads based on this analysis")

@cli.command("find-leads")
@click.option("--count", "-c", default=10, help="Number of leads to find")
@click.option("--product", "-p", help="Description of your product or service")
@click.option("--analysis-file", "-f", default="data/latest_analysis.txt", 
              help="Path to previously saved analysis file")
def find_leads(count: int, product: Optional[str], analysis_file: str):
    """Find leads based on product analysis."""
    target_audience = {}
    
    # If product is provided, analyze it first
    if product:
        analysis = orchestrator.analyze_product(product)
        target_audience = analysis['target_audience']
    
    # Otherwise, try to load from file
    elif os.path.exists(analysis_file):
        click.echo(f"Loading previous analysis from {analysis_file}")
        # This is a simplified version - in a real app we'd parse the file properly
        target_audience = {
            "title": "Previous Analysis",
            "description": "Loaded from file",
            "industry": "From file",
            "company_size": "Any",
            "role": "Decision maker"
        }
    
    # If no product or file, prompt the user
    else:
        product = click.prompt("What product or service are you selling?")
        analysis = orchestrator.analyze_product(product)
        target_audience = analysis['target_audience']
    
    click.echo(f"Finding {count} leads for {target_audience['title']}...")
    leads = orchestrator.find_leads(target_audience, count)
    
    # Save leads to file
    output_path = orchestrator.save_leads(leads)
    
    # Display leads in a table format
    display_leads_table(leads)
    
    click.echo(f"\n✅ Found {len(leads)} leads")
    click.echo(f"💾 Saved to {output_path}")
    click.echo("\nRun 'lead-agent sequence' to create personalized outreach")

@cli.command("sequence")
@click.option("--file", "-f", default=None, help="Path to leads file")
@click.option("--template", "-t", default=None, help="Message template")
def sequence(file: Optional[str], template: Optional[str]):
    """Create personalized outreach sequences for leads."""
    # Find the latest leads file if none provided
    if not file:
        # Look for most recent file in data directory
        data_dir = "data"
        if os.path.exists(data_dir):
            files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) 
                     if f.endswith('.csv') or f.endswith('.json')]
            if files:
                file = max(files, key=os.path.getmtime)
    
    if not file or not os.path.exists(file):
        click.echo("❌ No leads file found. Run 'lead-agent find-leads' first.")
        return
    
    # Load leads from file
    if file.endswith('.csv'):
        df = pd.read_csv(file)
        leads = df.to_dict('records')
    elif file.endswith('.json'):
        import json
        with open(file, 'r') as f:
            leads = json.load(f)
    else:
        click.echo(f"❌ Unsupported file format: {file}")
        return
    
    # Display leads and let user select
    display_leads_table(leads)
    
    # Get template if not provided
    if not template:
        template = click.prompt(
            "Enter your message template (use {name}, {company}, {insight} as placeholders)",
            default="Hi {name}, I noticed {company} is {insight}. I'd love to show you how our product can help."
        )
    
    # Let user select leads
    click.echo("\nSelect leads to include in sequence:")
    click.echo("1. All leads")
    click.echo("2. Select specific leads")
    choice = click.prompt("Enter your choice", type=int, default=1)
    
    selected_ids = None
    if choice == 2:
        # Get lead IDs from user
        id_input = click.prompt("Enter lead IDs separated by commas (e.g. 1,3,5)")
        selected_ids = [id.strip() for id in id_input.split(",")]
    
    # Generate personalized messages
    messages = orchestrator.generate_personalized_sequences(leads, template, selected_ids)
    
    # Display personalized messages
    click.echo("\n✅ Personalized Sequences Generated:")
    click.echo("=" * 50)
    for lead_id, message in messages.items():
        lead = next((l for l in leads if str(l.get("id")) == str(lead_id)), None)
        if lead:
            click.echo(f"\n📧 To: {lead.get('name')} ({lead.get('company')})")
            click.echo(f"Subject: Introduction from [Your Company]")
            click.echo("-" * 50)
            click.echo(message)
            click.echo("-" * 50)
    
    # Save messages to file
    output_dir = "data/sequences"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, f"sequences_{os.path.basename(file).split('.')[0]}.txt")
    with open(output_file, "w") as f:
        for lead_id, message in messages.items():
            lead = next((l for l in leads if str(l.get("id")) == str(lead_id)), None)
            if lead:
                f.write(f"To: {lead.get('name')} ({lead.get('company')})\n")
                f.write(f"Subject: Introduction from [Your Company]\n")
                f.write("-" * 50 + "\n")
                f.write(message + "\n")
                f.write("-" * 50 + "\n\n")
    
    click.echo(f"\n💾 Sequences saved to {output_file}")

def display_leads_table(leads: List[Dict[str, Any]]):
    """Display leads in a formatted table."""
    if not leads:
        click.echo("No leads found.")
        return
    
    # Convert to DataFrame for prettier display
    df = pd.DataFrame(leads)
    
    # Ensure essential columns exist
    essential_cols = ['id', 'name', 'title', 'company', 'email', 'linkedin']
    for col in essential_cols:
        if col not in df.columns:
            df[col] = ""
    
    # Select columns to display
    display_cols = [c for c in essential_cols if c in df.columns]
    
    # Add insights column if it exists
    if 'insights' in df.columns:
        display_cols.append('insights')
    
    # Limit string length for display
    for col in display_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).apply(lambda x: x[:40] + '...' if len(x) > 40 else x)
    
    # Print the table
    click.echo("\n📋 Leads:")
    click.echo(df[display_cols].to_string(index=False))

def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()