from openai import OpenAI
from typing import List, Dict, Optional
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LLM Configuration
LLM_CONFIG = {
    "Primary": {
        "api_key": "LLM_API_KEY",
        "base_url": "BASE_URL",
        "model": "LLM_MODEL",
        "default_model": "o1-preview"
    },
    "Secondary": {
        "api_key": "SECONDARY_LLM_API_KEY",
        "base_url": "SECONDARY_BASE_URL",
        "model": "SECONDARY_LLM_MODEL",
        "default_model": "o1-preview"
    }
}

def create_content(prompt: str) -> Optional[str]:
    """
    Create content using LLM with fallback to secondary model.
    
    Args:
        prompt (str): The input prompt for content generation
        
    Returns:
        Optional[str]: Generated content or None if both models fail
    """
    messages = [{"role": "user", "content": prompt}]

    response = call_llm(messages)
    if not response:
        logger.info("Primary model failed, attempting with secondary model")
        response = call_llm(messages, "Secondary")
    
    return response

def call_llm(messages: List[Dict[str, str]], model_type: str = "Primary", retries: int = 3) -> Optional[str]:
    """
    Call the LLM API with retry mechanism.
    
    Args:
        messages (List[Dict[str, str]]): List of message dictionaries
        model_type (str): Type of model to use ("Primary" or "Secondary")
        retries (int): Number of retry attempts
        
    Returns:
        Optional[str]: Generated content or None if all attempts fail
    """
    config = LLM_CONFIG.get(model_type)
    if not config:
        logger.error(f"Invalid model type: {model_type}")
        return None

    client = OpenAI(
        api_key=os.getenv(config["api_key"]),
        base_url=os.getenv(config["base_url"], "https://api.openai.com/v1")
    )
    model = os.getenv(config["model"], config["default_model"])

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Attempt #{attempt+1} | {model} Model: Failed to generate content - {str(e)}")
    
    return None
