"""
Company website scraper for Lead Agent.
"""
import logging
import re
import time
from typing import Dict, List, Any
from urllib.parse import urlparse, urljoin
import uuid

import requests
from bs4 import BeautifulSoup

from lead_agent.scraper.base import BaseScraper

logger = logging.getLogger(__name__)

class CompanyWebsiteScraper(BaseScraper):
    """Scraper that extracts contact information from company websites."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the company website scraper."""
        super().__init__(config)
        self.timeout = config.get("request_timeout", 10)
        self.max_retries = config.get("max_retries", 3)
        self.delay = config.get("request_delay", 2)
    
    def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape a company website for contact information.
        
        Args:
            url: Website URL
            
        Returns:
            Dictionary with company and contact information
        """
        headers = self._get_headers()
        proxies = self._get_proxy()
        
        # Extract domain for company name
        domain = urlparse(url).netloc
        company_name = domain.split(".")[-2] if len(domain.split(".")) > 1 else domain
        company_name = company_name.replace("-", " ").replace("_", " ").title()
        
        contacts = []
        pages_to_check = ["", "/about", "/contact", "/team", "/about-us", "/contact-us", "/our-team"]
        
        for page in pages_to_check:
            page_url = urljoin(url, page)
            try:
                logger.info(f"Scraping {page_url}")
                response = requests.get(
                    page_url,
                    headers=headers,
                    proxies=proxies,
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {page_url}: {response.status_code}")
                    continue
                
                # Extract contact information
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Find email addresses
                emails = self._extract_emails(soup)
                
                # Find phone numbers
                phones = self._extract_phones(soup)
                
                # Find team members/employees
                people = self._extract_people(soup)
                
                # Add generic company contact
                if emails or phones:
                    contact = {
                        "id": str(uuid.uuid4()),
                        "name": f"{company_name} Contact",
                        "email": emails[0] if emails else "",
                        "phone": phones[0] if phones else "",
                        "company": company_name,
                        "title": "Contact",
                        "linkedin": "",
                        "website": url,
                        "source": page_url
                    }
                    contacts.append(contact)
                
                # Add team members
                for person in people:
                    person_contact = {
                        "id": str(uuid.uuid4()),
                        "name": person.get("name", ""),
                        "email": person.get("email", ""),
                        "phone": person.get("phone", ""),
                        "company": company_name,
                        "title": person.get("title", ""),
                        "linkedin": person.get("linkedin", ""),
                        "website": url,
                        "source": page_url
                    }
                    contacts.append(person_contact)
                
                # Add a delay between requests
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error scraping {page_url}: {str(e)}")
        
        return contacts
    
    def _extract_emails(self, soup: BeautifulSoup) -> List[str]:
        """Extract email addresses from page."""
        emails = []
        
        # Method 1: Direct email links
        for link in soup.find_all("a"):
            href = link.get("href", "")
            if href.startswith("mailto:"):
                email = href[7:].split("?")[0].strip()
                if email and email not in emails:
                    emails.append(email)
        
        # Method 2: Text content
        text = soup.get_text()
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        found_emails = re.findall(email_pattern, text)
        
        for email in found_emails:
            if email not in emails:
                emails.append(email)
        
        return emails
    
    def _extract_phones(self, soup: BeautifulSoup) -> List[str]:
        """Extract phone numbers from page."""
        phones = []
        
        # Method 1: Phone links
        for link in soup.find_all("a"):
            href = link.get("href", "")
            if href.startswith("tel:"):
                phone = href[4:].strip()
                if phone and phone not in phones:
                    phones.append(phone)
        
        # Method 2: Text content
        text = soup.get_text()
        
        # Pattern for international numbers
        intl_pattern = r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        found_intl = re.findall(intl_pattern, text)
        
        # Pattern for US numbers
        us_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        found_us = re.findall(us_pattern, text)
        
        # Combine and deduplicate
        for phone in found_intl + found_us:
            if phone not in phones:
                phones.append(phone)
        
        return phones
    
    def _extract_people(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract team members/employees from page."""
        people = []
        
        # Look for common team/about page patterns
        team_sections = []
        
        # Method 1: Look for sections with team-related class/id
        team_keywords = ["team", "staff", "employees", "management", "leadership", "directors", "about-us"]
        for keyword in team_keywords:
            for section in soup.find_all(["div", "section"], class_=lambda c: c and keyword in c.lower()):
                team_sections.append(section)
            for section in soup.find_all(["div", "section"], id=lambda i: i and keyword in i.lower()):
                team_sections.append(section)
        
        # If no dedicated sections found, use the whole page
        if not team_sections:
            team_sections = [soup]
        
        # Extract people from sections
        for section in team_sections:
            # Method 1: Look for person cards/elements
            person_elements = []
            
            # Find elements with person-related classes
            person_keywords = ["person", "member", "employee", "profile", "card", "bio"]
            for keyword in person_keywords:
                elements = section.find_all(["div", "article", "li"], class_=lambda c: c and keyword in c.lower())
                person_elements.extend(elements)
            
            # Process each potential person element
            for element in person_elements:
                person = {}
                
                # Extract name
                name_element = element.find(["h2", "h3", "h4", "h5", "strong", "b"])
                if name_element:
                    person["name"] = name_element.get_text().strip()
                
                # Extract title
                title_elements = element.find_all("p")
                if title_elements:
                    person["title"] = title_elements[0].get_text().strip()
                
                # Extract email
                emails = self._extract_emails(element)
                if emails:
                    person["email"] = emails[0]
                
                # Extract phone
                phones = self._extract_phones(element)
                if phones:
                    person["phone"] = phones[0]
                
                # Extract LinkedIn
                linkedin = ""
                for link in element.find_all("a"):
                    href = link.get("href", "")
                    if "linkedin.com" in href:
                        linkedin = href
                        break
                person["linkedin"] = linkedin
                
                # Add person if we have at least a name
                if person.get("name"):
                    people.append(person)
        
        return people
    
    def scrape_leads(self, search_queries: List[str], count: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape leads based on search queries.
        
        Args:
            search_queries: List of search queries
            count: Number of leads to find
            
        Returns:
            List of lead dictionaries
        """
        # For this scraper, search_queries should be website URLs
        all_leads = []
        
        for url in search_queries:
            if