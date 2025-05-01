"""
Anthropic Claude integration for Lead Agent.
"""
import json
import logging
from typing import Dict, List, Any, Optional

import anthropic
from lead_agent.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Anthropic provider.
        
        Args:
            config: Configuration dictionary
        """
        self.api_key = config.get("api_key")
        self.model = config.get("model", "claude-3-haiku-20240307")
        
        if not self.api_key:
            logger.warning("Anthropic API key not found. Some functionality may not work.")
        
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
    
    def _call_model(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the Anthropic API.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            
        Returns:
            Model response text
        """
        if not self.client:
            raise ValueError("Anthropic client not initialized. Check your API key.")
        
        try:
            response = self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4000
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            raise
    
    def analyze_product(self, product_description: str) -> Dict[str, Any]:
        """
        Analyze a product description and recommend target audience.
        
        Args:
            product_description: Description of the product/service
            
        Returns:
            Dict containing target audience, markets, and outreach strategies
        """
        system_prompt = (
            "You are an expert in marketing, sales, and business development. "
            "Your task is to analyze product descriptions and identify ideal target audiences, "
            "market segments, and effective outreach strategies."
        )
        
        user_prompt = f"""
        Please analyze this product/service description and provide recommendations:
        
        PRODUCT DESCRIPTION:
        {product_description}
        
        Provide the following in JSON format:
        1. Target audience (title, description, industry, company_size, role)
        2. Top 3-5 markets to focus on (name, description)
        3. 3-5 outreach strategies (name, description)
        4. 10 search keywords to find potential leads
        
        Format your response as a valid JSON object with these keys: target_audience, markets, outreach_strategies, search_keywords
        Do not include any explanatory text before or after the JSON.
        """
        
        response = self._call_model(system_prompt, user_prompt)
        
        try:
            # Extract JSON from response
            json_str = response.strip()
            result = json.loads(json_str)
            
            # Ensure required keys exist
            required_keys = ["target_audience", "markets", "outreach_strategies", "search_keywords"]
            for key in required_keys:
                if key not in result:
                    result[key] = []
            
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from response: {response}")
            # Fall back to a basic structure
            return {
                "target_audience": {
                    "title": "General Business",
                    "description": "Could not parse target audience from model response",
                    "industry": "Various",
                    "company_size": "Any",
                    "role": "Decision maker"
                },
                "markets": [],
                "outreach_strategies": [],
                "search_keywords": []
            }
    
    def generate_search_queries(self, target_audience: Dict[str, Any]) -> List[str]:
        """
        Generate search queries based on target audience.
        
        Args:
            target_audience: Target audience profile
            
        Returns:
            List of search queries
        """
        system_prompt = (
            "You are an expert in search engine optimization and lead generation. "
            "Your task is to generate effective search queries to find potential leads "
            "based on a target audience profile."
        )
        
        user_prompt = f"""
        Given this target audience profile, generate 10 effective search queries to find potential leads:
        
        TARGET AUDIENCE:
        {json.dumps(target_audience, indent=2)}
        
        Create search queries that would help find decision-makers, companies, and professionals matching this profile.
        Format your response as a JSON array of strings, each being a search query.
        Do not include any explanatory text before or after the JSON array.
        """
        
        response = self._call_model(system_prompt, user_prompt)
        
        try:
            # Extract JSON from response
            json_str = response.strip()
            queries = json.loads(json_str)
            return queries if isinstance(queries, list) else []
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from response: {response}")
            # Fall back to basic queries based on the target audience
            return [
                f"{target_audience.get('industry', 'business')} companies",
                f"{target_audience.get('role', 'decision maker')} contacts",
            ]
    
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
        # Process in batches to avoid overwhelming the API
        enriched_leads = []
        batch_size = 5
        
        # Process leads in batches
        for i in range(0, len(leads), batch_size):
            batch = leads[i:i+batch_size]
            
            system_prompt = (
                "You are an expert in sales intelligence and lead enrichment. "
                "Your task is to analyze lead information and provide valuable insights "
                "that could help with personalized outreach."
            )
            
            user_prompt = f"""
            Given these leads and target audience profile, provide an insight for each lead:
            
            TARGET AUDIENCE:
            {json.dumps(target_audience, indent=2)}
            
            LEADS:
            {json.dumps(batch, indent=2)}
            
            For each lead, generate a personalized insight about why they might be interested in our product.
            Format your response as a JSON object where keys are lead IDs and values are insight strings.
            Do not include any explanatory text before or after the JSON.
            """
            
            response = self._call_model(system_prompt, user_prompt)
            
            try:
                # Extract JSON from response
                json_str = response.strip()
                insights = json.loads(json_str)
                
                # Add insights to leads
                for lead in batch:
                    lead_id = str(lead.get("id", ""))
                    if lead_id in insights:
                        lead["insight"] = insights[lead_id]
                    enriched_leads.append(lead)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from response: {response}")
                # Add leads without enrichment
                enriched_leads.extend(batch)
        
        return enriched_leads
    
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
        system_prompt = (
            "You are an expert in sales copywriting and personalized outreach. "
            "Your task is to customize message templates for individual leads "
            "based on their profile and any available insights."
        )
        
        user_prompt = f"""
        Please personalize this message template for each lead:
        
        TEMPLATE:
        {template}
        
        LEADS:
        {json.dumps(leads, indent=2)}
        
        For each lead, create a personalized message based on the template.
        Replace placeholders like {{name}}, {{company}}, etc. with the corresponding values.
        If a placeholder doesn't have a matching field, use appropriate generic text.
        
        Format your response as a JSON object where keys are lead IDs and values are personalized messages.
        Do not include any explanatory text before or after the JSON.
        """
        
        response = self._call_model(system_prompt, user_prompt)
        
        try:
            # Extract JSON from response
            json_str = response.strip()
            messages = json.loads(json_str)
            return messages
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from response: {response}")
            # Fall back to basic message personalization
            messages = {}
            for lead in leads:
                lead_id = str(lead.get("id", ""))
                name = lead.get("name", "there")
                company = lead.get("company", "your company")
                
                # Basic template substitution
                message = template
                message = message.replace("{name}", name)
                message = message.replace("{company}", company)
                
                if "{insight}" in message and "insight" in lead:
                    message = message.replace("{insight}", lead["insight"])
                else:
                    message = message.replace("{insight}", "might be interested in our solution")
                
                messages[lead_id] = message
            
            return messages