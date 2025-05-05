"""
Lead enrichment module for Lead Agent.
"""
import logging
import re
import time
from typing import Dict, List, Any, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class LeadEnricher:
    """Enricher for lead data."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the lead enricher.
        
        Args:
            config: Enricher configuration
        """
        self.config = config
        self.delay = config.get("request_delay", 2)
        self.timeout = config.get("request_timeout", 10)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.9",
        }
    
    def enrich_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a single lead with additional information.
        
        Args:
            lead: Lead dictionary
            
        Returns:
            Enriched lead dictionary
        """
        enriched_lead = lead.copy()
        
        # Add company information if available
        if lead.get("company") and not lead.get("company_info"):
            company_info = self._get_company_info(lead["company"])
            if company_info:
                enriched_lead["company_info"] = company_info
        
        # Add LinkedIn profile information if available
        if lead.get("linkedin") and not lead.get("linkedin_info"):
            linkedin_info = self._get_linkedin_info(lead["linkedin"])
            if linkedin_info:
                enriched_lead["linkedin_info"] = linkedin_info
        
        # Generate insights based on available information
        if not lead.get("insight"):
            enriched_lead["insight"] = self._generate_insight(enriched_lead)
        
        return enriched_lead
    
    def enrich_leads(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich a list of leads with additional information.
        
        Args:
            leads: List of lead dictionaries
            
        Returns:
            List of enriched lead dictionaries
        """
        enriched_leads = []
        
        for lead in leads:
            enriched_lead = self.enrich_lead(lead)
            enriched_leads.append(enriched_lead)
            
            # Add a delay between requests
            time.sleep(self.delay)
        
        return enriched_leads
    
    def _get_company_info(self, company_name: str) -> Dict[str, Any]:
        """
        Get information about a company.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Company information dictionary
        """
        try:
            # Search for company information
            search_url = f"https://www.google.com/search?q={company_name.replace(' ', '+')}+company+information"
            
            response = requests.get(
                search_url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                return {}
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract company information from search results
            company_info = {
                "name": company_name,
                "description": "",
                "industry": "",
                "size": "",
                "founded": "",
                "location": ""
            }
            
            # Look for description
            description_divs = soup.find_all("div", class_=lambda c: c and "description" in c.lower())
            if description_divs:
                for div in description_divs:
                    text = div.get_text().strip()
                    if len(text) > 50 and len(text) < 500:
                        company_info["description"] = text
                        break
            
            # Look for industry
            industry_terms = ["industry", "sector", "field", "market"]
            for term in industry_terms:
                industry_elements = soup.find_all(text=re.compile(f"{term}:", re.IGNORECASE))
                if industry_elements:
                    for element in industry_elements:
                        parent = element.parent
                        if parent:
                            text = parent.get_text().strip()
                            industry_match = re.search(rf"{term}:\s*([^,\.]+)", text, re.IGNORECASE)
                            if industry_match:
                                company_info["industry"] = industry_match.group(1).strip()
                                break
                
                if company_info["industry"]:
                    break
            
            # Look for location
            location_terms = ["headquarters", "location", "based in", "hq"]
            for term in location_terms:
                location_elements = soup.find_all(text=re.compile(f"{term}", re.IGNORECASE))
                if location_elements:
                    for element in location_elements:
                        parent = element.parent
                        if parent:
                            text = parent.get_text().strip()
                            location_match = re.search(rf"{term}:?\s*([^,\.]+)", text, re.IGNORECASE)
                            if location_match:
                                company_info["location"] = location_match.group(1).strip()
                                break
                
                if company_info["location"]:
                    break
            
            # Look for company size
            size_terms = ["employees", "team size", "company size", "workforce"]
            for term in size_terms:
                size_elements = soup.find_all(text=re.compile(f"{term}", re.IGNORECASE))
                if size_elements:
                    for element in size_elements:
                        parent = element.parent
                        if parent:
                            text = parent.get_text().strip()
                            size_match = re.search(r'(\d+[\-\s]?\d*)\s+{}'.format(term), text, re.IGNORECASE)
                            if size_match:
                                company_info["size"] = size_match.group(1).strip()
                                break
                
                if company_info["size"]:
                    break
            
            # Look for founding date
            founded_terms = ["founded", "established", "started", "launched"]
            for term in founded_terms:
                founded_elements = soup.find_all(text=re.compile(f"{term}", re.IGNORECASE))
                if founded_elements:
                    for element in founded_elements:
                        parent = element.parent
                        if parent:
                            text = parent.get_text().strip()
                            founded_match = re.search(rf"{term}:?\s*in\s*(\d{{4}})", text, re.IGNORECASE)
                            if founded_match:
                                company_info["founded"] = founded_match.group(1).strip()
                                break
                
                if company_info["founded"]:
                    break
            
            return company_info
            
        except Exception as e:
            logger.error(f"Error getting company info for {company_name}: {str(e)}")
            return {}
    
    def _get_linkedin_info(self, linkedin_url: str) -> Dict[str, Any]:
        """
        Get information from a LinkedIn profile.
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            LinkedIn information dictionary
        """
        # Note: In a real implementation, you would need to use LinkedIn's API or
        # a proper scraping library like LinkedIn-API. This is just a placeholder.
        return {
            "url": linkedin_url,
            "profile_exists": True
        }
    
    def _generate_insight(self, lead: Dict[str, Any]) -> str:
        """
        Generate an insight based on lead information.
        
        Args:
            lead: Lead dictionary
            
        Returns:
            Insight string
        """
        insights = []
        
        # Add company-based insights
        company = lead.get("company", "")
        if company:
            insights.append(f"works at {company}")
        
        # Add title-based insights
        title = lead.get("title", "")
        if title:
            insights.append(f"serves as {title}")
        
        # Add industry-based insights
        industry = ""
        company_info = lead.get("company_info", {})
        if company_info and company_info.get("industry"):
            industry = company_info.get("industry")
            insights.append(f"is in the {industry} industry")
        
        # Add location-based insights
        location = ""
        if company_info and company_info.get("location"):
            location = company_info.get("location")
            insights.append(f"is based in {location}")
        
        # Add company size insights
        company_size = ""
        if company_info and company_info.get("size"):
            company_size = company_info.get("size")
            insights.append(f"has approximately {company_size} employees")
        
        # Combine insights into a coherent statement
        if insights:
            return ", ".join(insights)
        else:
            return "might be interested in your product"