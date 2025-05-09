"""
Type definitions for the scraper module.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseScraper(ABC):
    """Abstract base class for web scrapers."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the scraper with configuration.
        
        Args:
            config: Scraper configuration
        """
        self.config = config
    
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