"""
Factory for creating scrapers.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def create_scraper(config: Dict[str, Any]):
    """
    Create a scraper instance based on configuration.
    
    Args:
        config: Scraper configuration
        
    Returns:
        BaseScraper instance
    """
    # Import here to avoid circular imports
    from lead_agent.scraper.scraper_types import BaseScraper
    
    scraping_method = config.get("scraping_method", "enhanced")
    
    try:
        if scraping_method == "linkedin":
            from lead_agent.scraper.linkedin import LinkedInScraper
            return LinkedInScraper(config)
        elif scraping_method == "search_engines":
            from lead_agent.scraper.search_engines import SearchEngineScraper
            return SearchEngineScraper(config)
        elif scraping_method == "apify":
            from lead_agent.scraper.apify_scraper import ApifyScraper
            return ApifyScraper(config)
        else:
            # Default to the enhanced scraper
            from lead_agent.scraper.enhanced_scraper import EnhancedScraper
            return EnhancedScraper(config)
    except ImportError as e:
        logger.error(f"Error importing scraper: {str(e)}")
        
        # Define a dummy scraper that returns empty results
        class DummyScraper(BaseScraper):
            def scrape_leads(self, search_queries, count=10):
                logger.warning("Using dummy scraper due to import error")
                return []
                
        return DummyScraper(config)