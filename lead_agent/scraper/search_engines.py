"""
Search engine scraper for Lead Agent.
"""
import logging
import time
import re
import random
from typing import Dict, List, Any
import uuid

import requests
from bs4 import BeautifulSoup

from lead_agent.scraper.base import BaseScraper

logger = logging.getLogger(__name__)

class SearchEngineScraper(BaseScraper):
    """Scraper that uses search engines to find leads."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the search engine scraper."""
        super().__init__(config)
        self.search_engines = [
            "https://www.google.com/search?q=",
            "https://www.bing.com/search?q=",
        ]
        self.timeout = config.get("request_timeout", 10)
        self.max_retries = config.get("max_retries", 3)
        self.delay = config.get("request_delay", 2)
    
    def _search(self, query: str) -> List[str]:
        """
        Perform a search and return result URLs.
        
        Args:
            query: Search query
            
        Returns:
            List of result URLs
        """
        search_url = random.choice(self.search_engines) + query.replace(" ", "+")
        headers = self._get_headers()
        proxies = self._get_proxy()
        
        try:
            logger.info(f"Searching for: {query}")
            response = requests.get(
                search_url,
                headers=headers,
                proxies=proxies,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.warning(f"Search failed with status code: {response.status_code}")
                return []
            
            # Extract links from the search results
            soup = BeautifulSoup(response.text, "html.parser")
            result_links = []
            
            # This is a simplified link extraction that needs to be adapted
            # for different search engines
            for link in soup.find_all("a"):
                href = link.get("href", "")
                # Filter for actual result links (highly simplified)
                if href.startswith("http") and not href.startswith(("https://www.google", "https://www.bing")):
                    result_links.append(href)
            
            logger.info(f"Found {len(result_links)} results for query: {query}")
            return result_links[:10]  # Limit to top 10 results
            
        except Exception as e:
            logger.error(f"Error searching for {query}: {str(e)}")
            return []
    
    def _extract_contact_info(self, url: str) -> Dict[str, Any]:
        """
        Extract contact information from a webpage.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with contact information
        """
        headers = self._get_headers()
        proxies = self._get_proxy()
        
        try:
            logger.info(f"Extracting contact info from: {url}")
            response = requests.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {url}: {response.status_code}")
                return {}
            
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            
            # Extract email addresses (basic pattern)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            
            # Extract phone numbers (simplified)
            phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
            
            # Extract names (very simplified approach)
            # This would need to be much more sophisticated in practice
            potential_names = []
            for paragraph in soup.find_all('p'):
                p_text = paragraph.get_text()
                # Look for common name patterns like "Name:" or "Contact:"
                if re.search(r'\b(Name|Contact|Person|Manager|Director)\s*:', p_text, re.I):
                    potential_names.append(p_text)
            
            # Extract company name (simplified)
            company = ""
            title_tag = soup.find('title')
            if title_tag:
                company = title_tag.get_text().split('-')[0].strip()
                if len(company) > 50:  # Probably not a company name
                    company = ""
            
            # Create basic contact information
            contact = {
                "id": str(uuid.uuid4()),
                "name": potential_names[0] if potential_names else "",
                "email": emails[0] if emails else "",
                "phone": phones[0] if phones else "",
                "company": company,
                "title": "",
                "linkedin": "",
                "website": url,
                "source": url
            }
            
            return contact
            
        except Exception as e:
            logger.error(f"Error extracting contact info from {url}: {str(e)}")
            return {}
    
    def scrape_leads(self, search_queries: List[str], count: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape leads based on search queries.
        
        Args:
            search_queries: List of search queries
            count: Number of leads to find
            
        Returns:
            List of lead dictionaries
        """
        leads = []
        urls_processed = set()
        
        # Process each search query
        for query in search_queries:
            if len(leads) >= count:
                break
                
            # Search for results
            result_urls = self._search(query)
            
            # Add a delay between searches
            time.sleep(self.delay)
            
            # Process each result URL
            for url in result_urls:
                if len(leads) >= count:
                    break
                    
                if url in urls_processed:
                    continue
                    
                urls_processed.add(url)
                
                # Extract contact information
                contact = self._extract_contact_info(url)
                
                if contact and contact.get("email") or contact.get("phone"):
                    leads.append(contact)
                
                # Add a delay between requests
                time.sleep(self.delay)
        
        logger.info(f"Scraped {len(leads)} leads from search queries")
        return leads[:count]  # Ensure we don't exceed the requested count