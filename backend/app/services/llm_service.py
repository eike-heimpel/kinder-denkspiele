"""LLM service for OpenRouter API integration."""

import json
import logging
from typing import Any, Dict, List
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMService:
    """Service for interacting with OpenRouter API."""

    def __init__(self):
        """Initialize the LLM service."""
        self.api_key = settings.openrouter_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost:5173",
            "X-Title": "Maerchenweber",  # ASCII only for HTTP headers
        }

    async def generate_text(
        self,
        prompt: str,
        model: str,
        sampling_params: Dict[str, Any] | None = None,
        json_mode: bool = False,
        json_schema: Dict[str, Any] | None = None,
    ) -> str:
        """Generate text using the OpenRouter API.

        Args:
            prompt: The prompt to send to the LLM
            model: Model identifier (e.g., 'google/gemini-2.0-flash-exp:free')
            sampling_params: Optional sampling parameters (temperature, top_p, etc.)
            json_mode: If True, request JSON output format
            json_schema: Optional custom JSON schema (if not provided, uses default story schema)

        Returns:
            Generated text response

        Raises:
            httpx.HTTPError: If the API request fails
        """
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }

        # Add sampling parameters
        if sampling_params:
            payload.update(sampling_params)

        # Request JSON response format with schema
        if json_mode:
            if json_schema:
                # Use custom schema if provided
                payload["response_format"] = {
                    "type": "json_schema",
                    "json_schema": json_schema
                }
            else:
                # Default story schema
                payload["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "story_response",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "story_text": {
                                    "type": "string",
                                    "description": "The story text in German"
                                },
                                "image_prompt": {
                                    "type": "string",
                                    "description": "Image description in German"
                                }
                            },
                            "required": ["story_text", "image_prompt"],
                            "additionalProperties": False
                        }
                    }
                }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                logger.info(f"Calling OpenRouter API with model: {model}")
                response = await client.post(
                    OPENROUTER_API_URL,
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

                logger.info(f"API response status: {response.status_code}")
                logger.info(f"API response keys: {result.keys()}")

                # Check for errors in response
                if "error" in result:
                    logger.error(f"API returned error: {result['error']}")
                    raise ValueError(f"API error: {result['error'].get('message', 'Unknown error')}")

                # Extract the content from the response
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    logger.info(f"Extracted content (first 100 chars): {content[:100] if content else 'EMPTY/NULL'}")

                    if not content:
                        logger.error(f"Content is empty! Full response: {result}")
                        raise ValueError("Empty content in API response")

                    return content.strip()
                else:
                    logger.error(f"No choices in response. Full response: {result}")
                    raise ValueError("No choices in API response")

            except httpx.HTTPError as e:
                logger.error(f"OpenRouter API HTTP error: {str(e)}")
                logger.error(f"Response status: {response.status_code if 'response' in locals() else 'N/A'}")
                logger.error(f"Response text: {response.text[:500] if 'response' in locals() else 'N/A'}")
                raise
            except (KeyError, IndexError, ValueError) as e:
                logger.error(f"Failed to parse API response: {type(e).__name__}")
                logger.error(f"Error details: {str(e)}")
                if 'result' in locals():
                    logger.error(f"Response structure: {result}")
                raise ValueError("Invalid API response format")

    async def generate_image(
        self,
        prompt: str,
        model: str = "google/gemini-2.0-flash-exp:free",
        aspect_ratio: str = "1:1",
        previous_image_url: str | None = None,
        style_description: str | None = None,
    ) -> str:
        """Generate an image using OpenRouter API with optional style consistency.

        Args:
            prompt: The image generation prompt (in English)
            model: Model identifier for image generation
            aspect_ratio: Aspect ratio (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9)
            previous_image_url: Optional URL of previous image to maintain style consistency
            style_description: Optional text description of the style to maintain

        Returns:
            Image URL (base64 data URL or hosted URL)

        Raises:
            httpx.HTTPError: If the API request fails
        """
        # Build the content array for multimodal input
        content = []

        # Add style instructions if provided
        if style_description:
            enhanced_prompt = f"Continue in the same art style: {style_description}\n\n{prompt}"
        else:
            enhanced_prompt = prompt

        # Add text prompt
        content.append({
            "type": "text",
            "text": enhanced_prompt
        })

        # Add previous image if provided (for style consistency)
        if previous_image_url:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": previous_image_url
                }
            })
            logger.info(f"Including previous image for style consistency")

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": aspect_ratio},
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    OPENROUTER_API_URL,
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

                # Extract image URL from response
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0]["message"]

                    # Check for images in the response
                    if "images" in message and len(message["images"]) > 0:
                        image_data = message["images"][0]
                        image_url = image_data["image_url"]["url"]
                        return image_url
                    else:
                        logger.warning("No images in API response, returning placeholder")
                        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='600'%3E%3Crect width='800' height='600' fill='%23f3f4f6'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' fill='%236b7280' font-size='24'%3EMärchenweber%3C/text%3E%3C/svg%3E"
                else:
                    raise ValueError("No choices in API response")

            except httpx.HTTPError as e:
                logger.error(f"OpenRouter image generation error: {e}")
                # Return placeholder image on error
                return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='600'%3E%3Crect width='800' height='600' fill='%23f3f4f6'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' fill='%236b7280' font-size='24'%3EMärchenweber%3C/text%3E%3C/svg%3E"
            except (KeyError, IndexError, ValueError) as e:
                logger.error(f"Failed to parse image API response: {e}")
                return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='600'%3E%3Crect width='800' height='600' fill='%23f3f4f6'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' fill='%236b7280' font-size='24'%3EMärchenweber%3C/text%3E%3C/svg%3E"

    async def generate_parallel(
        self,
        prompts: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate multiple responses in parallel.

        Args:
            prompts: List of dicts with keys: 'prompt', 'model', 'sampling_params'

        Returns:
            List of generated text responses in the same order as prompts
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            tasks = []
            for item in prompts:
                payload = {
                    "model": item["model"],
                    "messages": [{"role": "user", "content": item["prompt"]}],
                }
                if "sampling_params" in item:
                    payload.update(item["sampling_params"])

                task = client.post(
                    OPENROUTER_API_URL,
                    headers=self.headers,
                    json=payload,
                )
                tasks.append(task)

            # Execute all requests in parallel
            responses = await httpx.AsyncClient().gather(*tasks)

            results = []
            for response in responses:
                try:
                    response.raise_for_status()
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        content = result["choices"][0]["message"]["content"]
                        results.append(content.strip())
                    else:
                        results.append("")
                except Exception as e:
                    logger.error(f"Failed to process parallel response: {e}")
                    results.append("")

            return results


def get_llm_service() -> LLMService:
    """Get an instance of the LLM service.

    Returns:
        LLMService instance
    """
    return LLMService()
