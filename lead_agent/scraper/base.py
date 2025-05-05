"""
Base scraper classes and factory for Lead Agent.
"""
import logging
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any

from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Abstract base class for web scrapers."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the scraper with configuration.
        
        Args:
            config: Scraper configuration
        """
        self.config = config
        self.user_agent = UserAgent()
        self.proxies = config.get("proxy_list", [])
        self.use_proxies = config.get("use_proxies", False) and len(self.proxies) > 0
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get randomized headers for requests.
        
        Returns:
            Dictionary of HTTP headers
        """
        return {
            "User-Agent": self.user_agent.random,
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
    
    def _get_proxy(self) -> Dict[str, str]:
        """
        Get a random proxy if enabled.
        
        Returns:
            Proxy dictionary or empty dict if not using proxies
        """
        if not self.use_proxies or not self.proxies:
            return {}
            
        proxy = random.choice(self.proxies)
        return {"http": proxy, "https": proxy}
    
    @abstractmethod
    def scrape_leads(self, search_queries: List[str], count: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape leads based on search queries.
        
        Args:
            search_queries: List of search queries
            count: Number of leads to find
            
        Returns:
            List of lead dictionaries
        """
        pass

class BaseScraperFactory:
    """Factory for creating scrapers."""
    
    @staticmethod
    def create_scraper(config: Dict[str, Any]) -> BaseScraper:
        """
        Create a scraper instance based on configuration.
        
        Args:
            config: Scraper configuration
            
        Returns:
            BaseScraper instance
        """
        # Import here to avoid circular imports
        from lead_agent.scraper.linkedin import LinkedInScraper
        from lead_agent.scraper.search_engines import SearchEngineScraper
        from lead_agent.scraper.enhanced_scraper import EnhancedScraper
        
        scraping_method = config.get("scraping_method", "enhanced")
        
        if scraping_method == "linkedin":
            return LinkedInScraper(config)
        elif scraping_method == "search_engines":
            return SearchEngineScraper(config)
        else:
            # Default to the enhanced scraper
            return EnhancedScraper(config)