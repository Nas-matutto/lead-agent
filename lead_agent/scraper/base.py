"""
Utility functions and factory for scrapers.
"""
import logging
import random
from typing import Dict, List, Any

from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

def get_headers() -> Dict[str, str]:
    """
    Get randomized headers for requests.
    
    Returns:
        Dictionary of HTTP headers
    """
    user_agent = UserAgent()
    return {
        "User-Agent": user_agent.random,
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

def get_proxy(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Get a random proxy if enabled.
    
    Args:
        config: Configuration with proxy settings
        
    Returns:
        Proxy dictionary or empty dict if not using proxies
    """
    proxies = config.get("proxy_list", [])
    use_proxies = config.get("use_proxies", False) and len(proxies) > 0
    
    if not use_proxies or not proxies:
        return {}
        
    proxy = random.choice(proxies)
    return {"http": proxy, "https": proxy}