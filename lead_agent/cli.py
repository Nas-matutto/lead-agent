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
        id_input = click.prompt("Enter lead selection numbers separated by commas (e.g. 1,3,5)")
        # Convert selection numbers to actual lead IDs
        selection_numbers = [int(id.strip()) for id in id_input.split(",")]
        selected_ids = [leads[num-1]["id"] for num in selection_numbers if 0 < num <= len(leads)]
    
    # Generate personalized messages
    personalized_content = orchestrator.generate_personalized_sequences(leads, template, selected_ids)
    
    # Display personalized messages
    click.echo("\n✅ Personalized Sequences Generated:")
    click.echo("=" * 60)
    
    for lead_id, content in personalized_content.items():
        lead = content["lead"]
        click.echo(f"\n📧 To: {lead.get('name', 'Contact')} ({lead.get('company', 'Company')})")
        click.echo(f"Subject: {content['subject']}")
        click.echo("-" * 60)
        click.echo(content["message"])
        click.echo("-" * 60)
    
    # Save messages to file
    output_dir = "data/sequences"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, f"sequences_{os.path.basename(file).split('.')[0]}.txt")
    with open(output_file, "w") as f:
        for lead_id, content in personalized_content.items():
            lead = content["lead"]
            f.write(f"To: {lead.get('name', 'Contact')} ({lead.get('company', 'Company')})\n")
            f.write(f"Subject: {content['subject']}\n")
            f.write("-" * 60 + "\n")
            f.write(content["message"] + "\n")
            f.write("-" * 60 + "\n\n")
    
    click.echo(f"\n💾 Sequences saved to {output_file}")

def display_leads_table(leads: List[Dict[str, Any]]):
    """Display leads in a formatted table with selection numbers."""
    if not leads:
        click.echo("No leads found.")
        return
    
    # Convert to DataFrame for prettier display
    df = pd.DataFrame(leads)
    
    # Add selection column
    df.insert(0, 'Select', range(1, len(df) + 1))
    
    # Ensure essential columns exist
    essential_cols = ['id', 'name', 'title', 'company', 'email', 'linkedin']
    for col in essential_cols:
        if col not in df.columns:
            df[col] = ""
    
    # Select columns to display
    display_cols = ['Select']
    display_cols.extend([c for c in ['name', 'company', 'title', 'email'] if c in df.columns])
    
    # Add insights column if it exists
    if 'insight' in df.columns:
        display_cols.append('insight')
    
    # Limit string length for display
    for col in display_cols:
        if col != 'Select' and df[col].dtype == 'object':
            df[col] = df[col].astype(str).apply(lambda x: (x[:37] + '...') if len(x) > 40 else x)
    
    # Format the table
    click.echo("\n📋 Leads:")
    
    # Create a formatted table with borders
    table_data = []
    table_data.append(display_cols)  # Header row
    
    for _, row in df[display_cols].iterrows():
        table_data.append(row.tolist())
    
    # Calculate column widths
    col_widths = [max(len(str(row[i])) for row in table_data) + 2 for i in range(len(display_cols))]
    
    # Print header
    header = '│' + '│'.join(f' {h:{w}} ' for h, w in zip(table_data[0], col_widths)) + '│'
    border = '┌' + '┬'.join('─' * (w + 2) for w in col_widths) + '┐'
    separator = '├' + '┼'.join('─' * (w + 2) for w in col_widths) + '┤'
    
    click.echo(border)
    click.echo(header)
    click.echo(separator)
    
    # Print data rows
    for row in table_data[1:]:
        data_row = '│' + '│'.join(f' {str(d):{w}} ' for d, w in zip(row, col_widths)) + '│'
        click.echo(data_row)
    
    # Print bottom border
    bottom_border = '└' + '┴'.join('─' * (w + 2) for w in col_widths) + '┘'
    click.echo(bottom_border)
    
    click.echo(f"\nTotal leads: {len(leads)}")
    click.echo("Use the 'Select' column numbers to choose leads when sending sequences.")

def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

@cli.command("filter")
@click.option("--file", "-f", default=None, help="Path to leads file")
@click.option("--keyword", "-k", help="Keyword to filter by")
@click.option("--field", "-fd", default="all", help="Field to filter on (name, company, email, all)")
def filter_leads(file: Optional[str], keyword: str, field: str):
    """Filter leads by keyword."""
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
    
    # Filter leads
    if field == "all":
        filtered_leads = []
        for lead in leads:
            for k, v in lead.items():
                if keyword.lower() in str(v).lower():
                    filtered_leads.append(lead)
                    break
    else:
        filtered_leads = [lead for lead in leads if keyword.lower() in str(lead.get(field, "")).lower()]
    
    # Display filtered leads
    display_leads_table(filtered_leads)
    
    # Save filtered leads
    if filtered_leads:
        output_path = orchestrator.save_leads(filtered_leads, format="csv")
        click.echo(f"\n💾 Filtered leads saved to {output_path}")

@cli.command("sort")
@click.option("--file", "-f", default=None, help="Path to leads file")
@click.option("--field", "-fd", default="company", help="Field to sort by")
@click.option("--reverse", "-r", is_flag=True, help="Sort in reverse order")
def sort_leads(file: Optional[str], field: str, reverse: bool):
    """Sort leads by field."""
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
    
    # Sort leads
    if field in leads[0]:
        sorted_leads = sorted(leads, key=lambda x: str(x.get(field, "")), reverse=reverse)
        
        # Display sorted leads
        display_leads_table(sorted_leads)
        
        # Save sorted leads
        output_path = orchestrator.save_leads(sorted_leads, format="csv")
        click.echo(f"\n💾 Sorted leads saved to {output_path}")
    else:
        click.echo(f"❌ Field '{field}' not found in leads. Available fields: {', '.join(leads[0].keys())}")