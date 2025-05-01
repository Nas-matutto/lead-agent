"""
Base classes and factories for LLM providers.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

from lead_agent.config import get_config

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def analyze_product(self, product_description: str) -> Dict[str, Any]:
        """
        Analyze a product description and recommend target audience.
        
        Args:
            product_description: Description of the product/service
            
        Returns:
            Dict containing target audience, markets, and outreach strategies
        """
        pass
    
    @abstractmethod
    def generate_search_queries(self, target_audience: Dict[str, Any]) -> List[str]:
        """
        Generate search queries based on target audience.
        
        Args:
            target_audience: Target audience profile
            
        Returns:
            List of search queries
        """
        pass
    
    @abstractmethod
    def enrich_leads(
        self, 
        leads: List[Dict[str, Any]], 
        target_audience: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Enrich leads with insights and additional information.
        
        Args:
            leads: List of lead dictionaries
            target_audience: Target audience profile
            
        Returns:
            List of enriched lead dictionaries
        """
        pass
    
    @abstractmethod
    def personalize_messages(
        self, 
        leads: List[Dict[str, Any]], 
        template: str
    ) -> Dict[str, str]:
        """
        Generate personalized messages for leads.
        
        Args:
            leads: List of lead dictionaries
            template: Message template
            
        Returns:
            Dictionary mapping lead IDs to personalized messages
        """
        pass

class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    @staticmethod
    def create_provider(provider_name: str) -> BaseLLMProvider:
        """
        Create an LLM provider instance by name.
        
        Args:
            provider_name: Name of the LLM provider
            
        Returns:
            An instance of BaseLLMProvider
        """
        config = get_config()["llm"]
        
        if provider_name == "anthropic":
            from lead_agent.llm.anthropic import AnthropicProvider
            return AnthropicProvider(config["anthropic"])
        elif provider_name == "openai":
            from lead_agent.llm.openai import OpenAIProvider
            return OpenAIProvider(config["openai"])
        elif provider_name == "deepseek":
            from lead_agent.llm.deepseek import DeepseekProvider
            return DeepseekProvider(config["deepseek"])
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """
        Get a list of available LLM providers.
        
        Returns:
            List of provider names
        """
        config = get_config()["llm"]
        return [name for name, cfg in config.items() if cfg.get("enabled", False)]


def get_default_llm_provider() -> BaseLLMProvider:
    """
    Get the default LLM provider based on configuration.
    
    Returns:
        An instance of BaseLLMProvider
    """
    available_providers = LLMProviderFactory.get_available_providers()
    
    if not available_providers:
        raise ValueError("No LLM providers are enabled. Check your configuration.")
    
    return LLMProviderFactory.create_provider(available_providers[0])