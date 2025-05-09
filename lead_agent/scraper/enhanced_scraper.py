"""
Enhanced scraper for Lead Agent that combines multiple scraping methods.
"""
import logging
import time
import random
import re
import uuid
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from lead_agent.scraper.scraper_types import BaseScraper
from lead_agent.scraper.base import get_headers, get_proxy

logger = logging.getLogger(__name__)

class EnhancedScraper(BaseScraper):
    """Enhanced scraper that combines multiple scraping methods."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the enhanced scraper."""
        super().__init__(config)
        self.timeout = config.get("request_timeout", 10)
        self.max_retries = config.get("max_retries", 3)
        self.delay = config.get("request_delay", 2)
        
        # Define search engines
        self.search_engines = [
            {"name": "Google", "url": "https://www.google.com/search?q="},
            {"name": "Bing", "url": "https://www.bing.com/search?q="}
        ]
        
        # Company domains to focus on (more business-oriented)
        self.company_domains = [
            "linkedin.com/company",
            "crunchbase.com/organization",
            ".io",
            ".ai",
            ".co",
            ".tech",
            ".app",
            ".inc",
            ".solutions",
            ".agency",
            ".studio",
            ".consulting"
        ]
        
        # List of executive titles to search for
        self.executive_titles = [
            "CEO", "CTO", "CFO", "COO", "CMO", "CRO", "CSO", 
            "Chief Executive Officer", "Chief Technology Officer", 
            "Chief Financial Officer", "Chief Operating Officer",
            "VP of", "Vice President", "Director of", "Head of",
            "Founder", "Co-founder", "President", "Partner"
        ]
        
        # List of generic emails to filter out
        self.generic_emails = [
            "info@", "contact@", "hello@", "admin@", "support@",
            "sales@", "marketing@", "help@", "team@", "no-reply@"
        ]
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Check if an email is valid and not generic.
        
        Args:
            email: Email address to check
            
        Returns:
            True if the email is valid and not generic
        """
        if not email or "@" not in email:
            return False
            
        # Check for valid email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False
            
        # Filter out generic emails
        if any(generic in email.lower() for generic in self.generic_emails):
            return False
            
        # Check for business domain (not gmail, yahoo, etc.)
        domain = email.split("@")[1].lower()
        personal_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com"]
        if domain in personal_domains:
            return False
            
        return True
    
    def _enhance_search_query(self, query: str, target_audience: Dict[str, Any]) -> List[str]:
        """
        Enhance a search query based on target audience.
        
        Args:
            query: Base search query
            target_audience: Target audience dictionary
            
        Returns:
            List of enhanced queries
        """
        enhanced_queries = []
        
        # Add the base query
        enhanced_queries.append(query)
        
        # Extract industry information
        industry = target_audience.get("industry", "")
        
        # Add industry-specific queries
        if industry:
            enhanced_queries.append(f"{query} {industry}")
            enhanced_queries.append(f"{industry} companies {query}")
        
        # Add role-specific queries
        role = target_audience.get("role", "")
        if role:
            enhanced_queries.append(f"{query} {role}")
            
            # Add executive-specific queries
            for title in self.executive_titles:
                enhanced_queries.append(f"{title} {industry} {query}")
        
        # Add business-specific queries
        enhanced_queries.append(f"{query} business")
        enhanced_queries.append(f"{query} company")
        enhanced_queries.append(f"{query} enterprise")
        enhanced_queries.append(f"{query} firm")
        
        # Add contact-oriented queries
        enhanced_queries.append(f"{query} team contact")
        enhanced_queries.append(f"{query} leadership team")
        enhanced_queries.append(f"{query} management team")
        
        # Return only unique queries
        return list(set(enhanced_queries))
    
    def _search(self, query: str, engine_index: int = 0) -> List[str]:
        """
        Perform a search and return result URLs.
        
        Args:
            query: Search query
            engine_index: Index of search engine to use
            
        Returns:
            List of result URLs
        """
        engine = self.search_engines[engine_index % len(self.search_engines)]
        search_url = engine["url"] + query.replace(" ", "+")
        headers = self._get_headers()
        proxies = self._get_proxy()
        
        try:
            logger.info(f"Searching for: {query} using {engine['name']}")
            
            # Add retry mechanism
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(
                        search_url,
                        headers=headers,
                        proxies=proxies,
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        break
                        
                    logger.warning(f"Search attempt {attempt + 1} failed with status code: {response.status_code}")
                    time.sleep(self.delay * (attempt + 1))  # Exponential backoff
                except requests.RequestException as e:
                    logger.warning(f"Search attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(self.delay * (attempt + 1))
            
            if response.status_code != 200:
                logger.warning(f"All search attempts failed for query: {query}")
                return []
            
            # Extract links from the search results
            soup = BeautifulSoup(response.text, "html.parser")
            result_links = []
            
            # Extract links with different patterns based on the search engine
            if engine["name"] == "Google":
                # Google search results
                for link in soup.find_all("a"):
                    href = link.get("href", "")
                    # Google prepends results with "/url?q="
                    if "/url?q=" in href and "google" not in href:
                        url = href.split("/url?q=")[1].split("&")[0]
                        if url not in result_links:
                            result_links.append(url)
            else:
                # Generic link extraction for other engines
                for link in soup.find_all("a"):
                    href = link.get("href", "")
                    if href.startswith("http") and all(domain not in href for domain in ["google.com", "bing.com"]):
                        if href not in result_links:
                            result_links.append(href)
            
            # Filter for company domains
            filtered_links = []
            for url in result_links:
                domain = urlparse(url).netloc
                path = urlparse(url).path
                
                # Prioritize company websites and LinkedIn company pages
                if any(company_domain in f"{domain}{path}" for company_domain in self.company_domains):
                    filtered_links.append(url)
            
            # Add other links if we don't have enough
            if len(filtered_links) < 10:
                for url in result_links:
                    if url not in filtered_links:
                        filtered_links.append(url)
                        if len(filtered_links) >= 10:
                            break
            
            logger.info(f"Found {len(filtered_links)} results for query: {query}")
            return filtered_links[:10]  # Limit to top 10 results
            
        except Exception as e:
            logger.error(f"Error searching for {query}: {str(e)}")
            return []
    
    def _extract_contact_info(self, url: str) -> List[Dict[str, Any]]:
        """
        Extract contact information from a webpage.
        
        Args:
            url: URL to scrape
            
        Returns:
            List of contact dictionaries
        """
        headers = self._get_headers()
        proxies = self._get_proxy()
        
        try:
            logger.info(f"Extracting contact info from: {url}")
            
            # Add retry mechanism
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(
                        url,
                        headers=headers,
                        proxies=proxies,
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        break
                        
                    logger.warning(f"Fetch attempt {attempt + 1} failed with status code: {response.status_code}")
                    time.sleep(self.delay * (attempt + 1))  # Exponential backoff
                except requests.RequestException as e:
                    logger.warning(f"Fetch attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(self.delay * (attempt + 1))
            
            if response.status_code != 200:
                logger.warning(f"All fetch attempts failed for URL: {url}")
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract company name
            company = self._extract_company_name(soup, url)
            
            # Extract text
            text = soup.get_text()
            
            # Extract emails (improved pattern)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            # Filter out invalid and generic emails
            valid_emails = [email for email in emails if self._is_valid_email(email)]
            
            # Extract phone numbers
            phones = self._extract_phone_numbers(text)
            
            # Extract LinkedIn profiles
            linkedin_profiles = self._extract_linkedin_profiles(soup)
            
            # Find people on the page
            people = self._extract_people(soup, text, company, valid_emails, phones, linkedin_profiles, url)
            
            # If no people found but we have emails, create contact entries
            if not people and valid_emails:
                for email in valid_emails[:3]:  # Limit to first 3 emails
                    name = self._extract_name_from_email(email, company)
                    
                    people.append({
                        "id": str(uuid.uuid4()),
                        "name": name,
                        "title": "",
                        "email": email,
                        "phone": phones[0] if phones else "",
                        "company": company,
                        "linkedin": "",
                        "website": url,
                        "source": url
                    })
            
            # If still no people but we have a company name, create a generic company contact
            if not people and company:
                people.append({
                    "id": str(uuid.uuid4()),
                    "name": f"{company} Contact",
                    "title": "",
                    "email": valid_emails[0] if valid_emails else "",
                    "phone": phones[0] if phones else "",
                    "company": company,
                    "linkedin": "",
                    "website": url,
                    "source": url
                })
            
            # Filter out contacts without email or phone
            filtered_people = [person for person in people if person.get("email") or person.get("phone")]
            
            return filtered_people
            
        except Exception as e:
            logger.error(f"Error extracting contact info from {url}: {str(e)}")
            return []
    
    def _extract_company_name(self, soup: BeautifulSoup, url: str) -> str:
        """Extract company name from page."""
        company = ""
        
        # Try to get from meta tags first
        og_site_name = soup.find("meta", property="og:site_name")
        if og_site_name and og_site_name.get("content"):
            company = og_site_name.get("content").strip()
        
        # Try title tag
        if not company:
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text()
                # Extract company name from title
                parts = [p.strip() for p in title_text.split('|')]
                if len(parts) > 1:
                    company = parts[0]
                else:
                    parts = [p.strip() for p in title_text.split('-')]
                    if len(parts) > 1:
                        company = parts[0]
                    else:
                        company = title_text.split('.')[0]
        
        # Clean up company name
        company = re.sub(r'\s*[|]\s*.*', '', company)
        company = re.sub(r'\s*[-]\s*.*', '', company)
        
        # Check for common patterns to remove
        company = re.sub(r'Home\s*[-|]\s*', '', company)
        company = re.sub(r'Homepage\s*[-|]\s*', '', company)
        company = re.sub(r'Welcome to\s*', '', company)
        
        # Fallback to domain name
        if not company or len(company) > 50:
            domain = urlparse(url).netloc
            company = domain.split('.')[0].capitalize()
        
        return company.strip()
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        phones = []
        
        # International format
        intl_phones = re.findall(r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', text)
        phones.extend(intl_phones)
        
        # US format
        us_phones = re.findall(r'(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', text)
        # Filter out invalid matches (too short)
        us_phones = [p for p in us_phones if len(re.sub(r'\D', '', p)) >= 7]
        phones.extend(us_phones)
        
        # Remove duplicates
        return list(set(phones))
    
    def _extract_linkedin_profiles(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract LinkedIn profile URLs."""
        profiles = {}
        
        # Find all links to LinkedIn profiles
        linkedin_links = soup.find_all("a", href=lambda href: href and "linkedin.com/in/" in href)
        
        for link in linkedin_links:
            href = link.get("href", "")
            
            # Try to extract the person's name
            name = ""
            # From link text
            if link.get_text().strip():
                name = link.get_text().strip()
            # From parent elements
            elif link.parent:
                parent_text = link.parent.get_text().strip()
                if parent_text and len(parent_text) < 50:  # Avoid grabbing huge text blocks
                    name = parent_text
            
            # Clean up name
            name = re.sub(r'LinkedIn|Profile|View|Connect|Follow|on LinkedIn', '', name).strip()
            
            if href and (name or "linkedin.com/in/" in href):
                profile_id = href.split("linkedin.com/in/")[1].split("/")[0].split("?")[0]
                profiles[profile_id] = {
                    "url": href,
                    "name": name
                }
        
        return profiles
    
    def _extract_name_from_email(self, email: str, company: str) -> str:
        """Extract name from email address."""
        try:
            username = email.split('@')[0]
            
            # Remove common prefixes
            username = re.sub(r'^(info|contact|sales|support|admin|help|team)', '', username)
            
            # Split by common separators
            parts = re.split(r'[._-]', username)
            parts = [p for p in parts if p]  # Remove empty parts
            
            if len(parts) >= 2:
                # Assume first and last name
                name = ' '.join(part.capitalize() for part in parts)
            elif len(parts) == 1:
                name = parts[0].capitalize()
            else:
                name = f"{company} Contact"
                
            return name
        except:
            return f"{company} Contact"
    
    def _extract_people(self, soup: BeautifulSoup, text: str, company: str, emails: List[str], phones: List[str], linkedin_profiles: Dict[str, Dict[str, str]], url: str) -> List[Dict[str, Any]]:
        """Extract people from the page."""
        people = []
        
        # Look for structured person blocks
        team_section_terms = ["team", "about us", "leadership", "management", "our people", "executives", "staff", "founders"]
        team_sections = []
        
        # Find sections that might contain team members
        for term in team_section_terms:
            # Look in headings
            for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                if term.lower() in heading.get_text().lower():
                    if heading.parent:
                        team_sections.append(heading.parent)
            
            # Look in divs with matching classes or IDs
            for div in soup.find_all("div", class_=lambda c: c and term.lower() in c.lower()):
                team_sections.append(div)
            
            for div in soup.find_all("div", id=lambda i: i and term.lower() in i.lower()):
                team_sections.append(div)
        
        # Process team sections
        person_blocks = []
        for section in team_sections:
            # Look for nested elements that might represent people
            for element in section.find_all(["div", "article", "section", "li"]):
                # Check if this element likely represents a person
                element_text = element.get_text().strip()
                
                # If too much text, it's probably not a person card
                if len(element_text) > 500:
                    continue
                
                # Check for executive titles
                has_title = any(title.lower() in element_text.lower() for title in self.executive_titles)
                
                # Check for email pattern
                has_email = any(email in element_text for email in emails)
                
                # Check for LinkedIn link
                has_linkedin = element.find("a", href=lambda href: href and "linkedin.com/in/" in href)
                
                # If it has a title, email, or LinkedIn, it's likely a person
                if has_title or has_email or has_linkedin:
                    person_blocks.append(element)
        
        # Process each person block
        for block in person_blocks:
            block_text = block.get_text().strip()
            
            # Try to extract name (usually in headings)
            name_elem = block.find(["h1", "h2", "h3", "h4", "h5", "h6", "strong", "b"])
            name = name_elem.get_text().strip() if name_elem else ""
            
            # If no name in headings, look for capitalized words
            if not name:
                name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})', block_text)
                if name_match:
                    name = name_match.group(1)
            
            # Try to extract title
            title = ""
            title_found = False
            
            # Look for common title patterns
            for exec_title in self.executive_titles:
                if exec_title.lower() in block_text.lower():
                    # Get the full title (title + extra words)
                    title_pattern = re.compile(rf'{re.escape(exec_title)}(?:\s+of\s+[\w\s]+)?', re.IGNORECASE)
                    title_match = title_pattern.search(block_text)
                    if title_match:
                        title = title_match.group(0)
                        title_found = True
                        break
            
            # If no standard title found, look for any capitalized words near the name
            if not title_found and name:
                name_index = block_text.find(name)
                if name_index >= 0:
                    after_name = block_text[name_index + len(name):].strip()
                    title_match = re.search(r'([A-Z][a-zA-Z]*(?:\s+[a-zA-Z]+){2,5})', after_name)
                    if title_match:
                        title = title_match.group(1)
            
            # Extract email from this block
            email = ""
            for e in emails:
                if e in block_text:
                    email = e
                    break
            
            # Extract phone from this block
            phone = ""
            for p in phones:
                if p in block_text:
                    phone = p
                    break
            
            # Extract LinkedIn
            linkedin = ""
            linkedin_link = block.find("a", href=lambda href: href and "linkedin.com/in/" in href)
            if linkedin_link:
                linkedin = linkedin_link["href"]
            
            if name:
                people.append({
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "title": title,
                    "email": email,
                    "phone": phone,
                    "company": company,
                    "linkedin": linkedin,
                    "website": url,
                    "source": url
                })
        
        # If few people found through structured blocks, try to match emails with LinkedIn profiles
        if len(people) < 3:
            # Try to create leads from LinkedIn profiles
            for profile_id, profile_data in linkedin_profiles.items():
                # Check if this person is already included
                if not any(p.get("linkedin") == profile_data["url"] for p in people):
                    people.append({
                        "id": str(uuid.uuid4()),
                        "name": profile_data["name"] or f"LinkedIn Profile {profile_id}",
                        "title": "",
                        "email": "",
                        "phone": "",
                        "company": company,
                        "linkedin": profile_data["url"],
                        "website": url,
                        "source": url
                    })
        
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
        leads = []
        urls_processed = set()
        
        # Use the first query to get target audience info (if available)
        target_audience = {
            "industry": "",
            "role": ""
        }
        
        # Generate enhanced search queries
        enhanced_queries = []
        for query in search_queries:
            enhanced_queries.extend(self._enhance_search_query(query, target_audience))
        
        # Shuffle queries to get more diverse results
        random.shuffle(enhanced_queries)
        
        # Process each search query
        for i, query in enumerate(enhanced_queries):
            if len(leads) >= count:
                break
                
            # Search for results using alternating search engines
            result_urls = self._search(query, i % len(self.search_engines))
            
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
                contacts = self._extract_contact_info(url)
                
                # Add valid contacts to leads
                for contact in contacts:
                    if contact.get("email") or contact.get("phone") or contact.get("linkedin"):
                        leads.append(contact)
                
                # Add a delay between requests
                time.sleep(self.delay)
        
        # Sort leads by quality (prioritize those with more contact info)
        def lead_quality_score(lead):
            score = 0
            if lead.get("email"):
                score += 10
            if lead.get("phone"):
                score += 5
            if lead.get("linkedin"):
                score += 3
            if lead.get("title"):
                score += 2
            return score
        
        leads.sort(key=lead_quality_score, reverse=True)
        
        logger.info(f"Scraped {len(leads)} leads from search queries")
        return leads[:count]  # Ensure we don't exceed the requested count