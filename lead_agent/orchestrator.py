"""
Core orchestration module for the Lead Agent.
Manages the workflow between different components.
"""
import logging
from typing import Dict, List, Any, Optional

from lead_agent.config import get_config
from lead_agent.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class LeadAgentOrchestrator:
    """Main orchestrator for the Lead Agent workflow."""
    
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        """Initialize the orchestrator with config and components."""
        self.config = get_config()
        self.llm_provider = llm_provider
        self._scraper = None
        self._processor = None
        self._storage = None
        self._initialized = False
        
    def initialize(self):
        """Lazy initialization of components."""
        if self._initialized:
            return
            
        # Import components here to avoid circular imports
        from lead_agent.scraper.base import BaseScraperFactory
        from lead_agent.processor.cleaner import DataProcessor
        from lead_agent.storage.exporter import DataExporter
        
        # Initialize components if not provided
        if not self.llm_provider:
            from lead_agent.llm.base import get_default_llm_provider
            self.llm_provider = get_default_llm_provider()
            
        self._scraper = BaseScraperFactory.create_scraper(self.config["scraping"])
        self._processor = DataProcessor(self.config["app"])
        self._storage = DataExporter(self.config["storage"])
        
        self._initialized = True
        logger.info("Lead Agent orchestrator initialized")
        
    def analyze_product(self, product_description: str) -> Dict[str, Any]:
        """
        Analyze the product and recommend target audience.
        
        Args:
            product_description: Description of the product/service
            
        Returns:
            Dict containing target audience, markets, and outreach strategies
        """
        self.initialize()
        
        logger.info(f"Analyzing product: {product_description[:50]}...")
        
        # Use LLM to analyze the product and generate recommendations
        product_analysis = self.llm_provider.analyze_product(product_description)
        
        return product_analysis
        
    def find_leads(self, target_audience: Dict[str, Any], count: int = 10) -> List[Dict[str, Any]]:
        """
        Find leads based on the target audience.
        
        Args:
            target_audience: Target audience profile
            count: Number of leads to find
            
        Returns:
            List of lead dictionaries
        """
        self.initialize()
        
        logger.info(f"Finding {count} leads for target audience: {target_audience['title']}")
        
        # Generate search queries based on target audience
        search_queries = self.llm_provider.generate_search_queries(target_audience)
        
        # Scrape the web for leads
        raw_leads = self._scraper.scrape_leads(search_queries, count)
        
        # Process and clean the leads
        processed_leads = self._processor.process_leads(raw_leads, target_audience)
        
        # Enrich leads with LLM-generated insights
        enriched_leads = self.llm_provider.enrich_leads(processed_leads, target_audience)
        
        return enriched_leads
        
    def save_leads(self, leads: List[Dict[str, Any]], format: str = None) -> str:
        """
        Save leads to the specified format.
        
        Args:
            leads: List of lead dictionaries
            format: Output format (csv, json, etc.)
            
        Returns:
            Path to the saved file
        """
        self.initialize()
        
        if not format:
            format = self.config["storage"]["default_format"]
            
        output_path = self._storage.export_leads(leads, format)
        logger.info(f"Saved {len(leads)} leads to {output_path}")
        
        return output_path
        
    def generate_personalized_sequences(
        self, 
        leads: List[Dict[str, Any]], 
        template: str, 
        selected_ids: List[str] = None
    ) -> Dict[str, str]:
        """
        Generate personalized sequence messages for selected leads.
        
        Args:
            leads: List of lead dictionaries
            template: Message template
            selected_ids: IDs of selected leads (if None, use all)
            
        Returns:
            Dictionary mapping lead IDs to personalized messages
        """
        self.initialize()
        
        # Filter leads if IDs are provided
        if selected_ids:
            filtered_leads = [lead for lead in leads if lead.get("id") in selected_ids]
        else:
            filtered_leads = leads
            
        logger.info(f"Generating personalized sequences for {len(filtered_leads)} leads")
        
        # Use LLM to personalize messages
        personalized_messages = self.llm_provider.personalize_messages(
            filtered_leads, 
            template
        )
        
        return personalized_messages