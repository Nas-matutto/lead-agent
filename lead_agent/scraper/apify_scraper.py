"""
Apify scraper for Lead Agent.
"""
import logging
import json
import requests
from typing import Dict, List, Any
import uuid
import time
import random

from lead_agent.scraper.scraper_types import BaseScraper
from lead_agent.scraper.base import get_headers, get_proxy

logger = logging.getLogger(__name__)

class ApifyScraper(BaseScraper):
    """Scraper that uses Apify to get high-quality leads from LinkedIn and other websites."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Apify scraper."""
        super().__init__(config)
        self.api_key = config.get("apify", {}).get("api_key", "")
        self.linkedin_actor_id = config.get("apify", {}).get("linkedin_actor_id", "apify/linkedin-scraper")
        self.website_actor_id = config.get("apify", {}).get("website_actor_id", "apify/website-content-crawler")
        
        if not self.api_key:
            logger.warning("Apify API key not found. Some functionality may not work.")
    
    def _scrape_linkedin(self, search_query: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape leads from LinkedIn using Apify.
        
        Args:
            search_query: LinkedIn search query
            count: Number of leads to find
            
        Returns:
            List of lead dictionaries
        """
        if not self.api_key:
            logger.error("Apify API key not provided")
            return []
            
        try:
            # Format the payload for Apify API
            payload = {
                "search": search_query,
                "maxItems": count
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Start the Apify task
            run_url = f"https://api.apify.com/v2/acts/{self.linkedin_actor_id}/runs"
            response = requests.post(
                run_url,
                json=payload,
                headers=headers
            )
            
            if response.status_code != 201:
                logger.error(f"Apify API error: {response.status_code} - {response.text}")
                return []
                
            run_data = response.json()
            run_id = run_data.get("data", {}).get("id")
            
            if not run_id:
                logger.error("Failed to get run ID from Apify")
                return []
            
            # Wait for the task to complete
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
            status = "RUNNING"
            max_attempts = 30
            attempts = 0
            
            while status == "RUNNING" and attempts < max_attempts:
                time.sleep(5)  # Wait 5 seconds between checks
                status_response = requests.get(
                    status_url,
                    headers=headers
                )
                
                if status_response.status_code != 200:
                    logger.error(f"Apify status check error: {status_response.status_code}")
                    break
                    
                status_data = status_response.json()
                status = status_data.get("data", {}).get("status")
                attempts += 1
            
            if status != "SUCCEEDED":
                logger.error(f"Apify task failed or timed out. Status: {status}")
                return []
            
            # Get the results
            dataset_id = status_data.get("data", {}).get("defaultDatasetId")
            results_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
            results_response = requests.get(
                results_url,
                headers=headers
            )
            
            if results_response.status_code != 200:
                logger.error(f"Apify results error: {results_response.status_code}")
                return []
                
            profiles = results_response.json()
            
            # Parse leads from the response
            leads = []
            
            for profile in profiles:
                lead = {
                    "id": str(uuid.uuid4()),
                    "name": profile.get("name", ""),
                    "title": profile.get("title", ""),
                    "company": profile.get("company", ""),
                    "location": profile.get("location", ""),
                    "linkedin": profile.get("profileUrl", ""),
                    "email": profile.get("email", ""),
                    "phone": profile.get("phone", ""),
                    "source": "linkedin",
                    "insight": profile.get("summary", "")
                }
                leads.append(lead)
                
                if len(leads) >= count:
                    break
            
            return leads
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn via Apify: {str(e)}")
            return []
    
    def _scrape_company_website(self, website_url: str) -> List[Dict[str, Any]]:
        """
        Scrape leads from a company website using Apify.
        
        Args:
            website_url: Company website URL
            
        Returns:
            List of lead dictionaries
        """
        if not self.api_key:
            logger.error("Apify API key not provided")
            return []
            
        try:
            # Format the payload for Apify API
            payload = {
                "startUrls": [{"url": website_url}],
                "maxCrawlPages": 20,
                "maxCrawlDepth": 2
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Start the Apify task
            run_url = f"https://api.apify.com/v2/acts/{self.website_actor_id}/runs"
            response = requests.post(
                run_url,
                json=payload,
                headers=headers
            )
            
            if response.status_code != 201:
                logger.error(f"Apify website scraper API error: {response.status_code} - {response.text}")
                return []
                
            run_data = response.json()
            run_id = run_data.get("data", {}).get("id")
            
            if not run_id:
                logger.error("Failed to get run ID from Apify for website scraping")
                return []
            
            # Wait for the task to complete
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
            status = "RUNNING"
            max_attempts = 30
            attempts = 0
            
            while status == "RUNNING" and attempts < max_attempts:
                time.sleep(5)  # Wait 5 seconds between checks
                status_response = requests.get(
                    status_url,
                    headers=headers
                )
                
                if status_response.status_code != 200:
                    logger.error(f"Apify website scraper status check error: {status_response.status_code}")
                    break
                    
                status_data = status_response.json()
                status = status_data.get("data", {}).get("status")
                attempts += 1
            
            if status != "SUCCEEDED":
                logger.error(f"Apify website scraper task failed or timed out. Status: {status}")
                return []
            
            # Get the results
            dataset_id = status_data.get("data", {}).get("defaultDatasetId")
            results_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
            results_response = requests.get(
                results_url,
                headers=headers
            )
            
            if results_response.status_code != 200:
                logger.error(f"Apify website scraper results error: {results_response.status_code}")
                return []
                
            pages = results_response.json()
            
            # Extract contact information from pages
            leads = []
            
            for page in pages:
                # Extract emails from page content
                emails = []
                if "html" in page:
                    import re
                    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                    emails = re.findall(email_pattern, page.get("html", ""))
                
                # Extract company name from URL
                from urllib.parse import urlparse
                domain = urlparse(website_url).netloc
                company_name = domain.split(".")[-2] if len(domain.split(".")) > 1 else domain
                company_name = company_name.replace("-", " ").replace("_", " ").title()
                
                # Create leads from emails
                for email in emails:
                    # Try to extract name from email
                    username = email.split('@')[0]
                    parts = re.split(r'[._-]', username)
                    name = ' '.join([p.capitalize() for p in parts if p])
                    
                    lead = {
                        "id": str(uuid.uuid4()),
                        "name": name or f"Contact at {company_name}",
                        "company": company_name,
                        "title": "Unknown",
                        "email": email,
                        "phone": "",
                        "linkedin": "",
                        "source": website_url,
                        "insight": f"Found on company website"
                    }
                    leads.append(lead)
            
            return leads
            
        except Exception as e:
            logger.error(f"Error scraping website via Apify: {str(e)}")
            return []
    
    def scrape_leads(self, search_queries: List[str], count: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape leads based on search queries.
        
        Args:
            search_queries: List of search queries
            count: Number of leads to find
            
        Returns:
            List of lead dictionaries
        """
        all_leads = []
        
        # Process LinkedIn queries
        linkedin_queries = [q for q in search_queries if "linkedin" in q.lower()]
        
        # If no specific LinkedIn queries, create some
        if not linkedin_queries and search_queries:
            # Create LinkedIn-specific variants of the existing queries
            linkedin_queries = [f"site:linkedin.com/in/ {q}" for q in search_queries[:2]]
        
        # Try LinkedIn queries first
        for query in linkedin_queries:
            try:
                logger.info(f"Scraping LinkedIn with query: {query}")
                leads = self._scrape_linkedin(query, count - len(all_leads))
                all_leads.extend(leads)
                
                if len(all_leads) >= count:
                    break
            except Exception as e:
                logger.error(f"Error scraping LinkedIn: {str(e)}")
        
        # Process website queries if we need more leads
        website_queries = [q for q in search_queries if "http" in q.lower()]
        if len(all_leads) < count:
            for query in website_queries:
                try:
                    logger.info(f"Scraping website: {query}")
                    leads = self._scrape_company_website(query)
                    all_leads.extend(leads)
                    
                    if len(all_leads) >= count:
                        break
                except Exception as e:
                    logger.error(f"Error scraping website: {str(e)}")
        
        # If we still don't have enough leads, try regular search queries
        if len(all_leads) < count:
            for query in search_queries:
                if "linkedin" not in query.lower() and "http" not in query.lower():
                    try:
                        # Modify query to focus on LinkedIn profiles
                        linkedin_query = f"site:linkedin.com/in/ {query}"
                        logger.info(f"Trying additional LinkedIn query: {linkedin_query}")
                        leads = self._scrape_linkedin(linkedin_query, count - len(all_leads))
                        all_leads.extend(leads)
                        
                        if len(all_leads) >= count:
                            break
                    except Exception as e:
                        logger.error(f"Error with additional LinkedIn query: {str(e)}")
        
        # If we still don't have any leads, return demo data
        if not all_leads:
            logger.warning("No leads found from Apify, returning demo data")
            # Generate demo leads
            companies = ["TechFlow Solutions", "Nova Digital", "Spark Creative", "Quantum Industries", "DataWave Systems"]
            roles = ["CEO", "CTO", "Marketing Director", "Project Manager", "Operations Lead"]
            insights = [
                "Recently expanded their team",
                "Looking for new productivity tools",
                "Managing multiple client projects",
                "Facing workflow challenges",
                "Planning digital transformation"
            ]
            
            for i in range(count):
                company = random.choice(companies)
                role = random.choice(roles)
                first_name = random.choice(["James", "Sarah", "Michael", "Emily", "David", "Jessica"])
                last_name = random.choice(["Smith", "Johnson", "Chen", "Rodriguez", "Taylor", "Kim"])
                
                lead = {
                    "id": str(uuid.uuid4()),
                    "name": f"{first_name} {last_name}",
                    "company": company,
                    "title": role,
                    "email": f"{first_name.lower()}.{last_name.lower()}@{company.lower().replace(' ', '')}.com",
                    "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    "linkedin": f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{random.randint(10000, 99999)}",
                    "source": "demo (Apify fallback)",
                    "insight": random.choice(insights)
                }
                all_leads.append(lead)
        
        # Return the leads we found, limited to the requested count
        return all_leads[:count]