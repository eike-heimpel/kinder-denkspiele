"""LLM service for OpenRouter API integration."""

import json
from typing import Any, Dict, List
import httpx
from app.config import settings
from app.logger import logger

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
                # Default story schema with 3 choices + characters
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
                                },
                                "choice_1": {
                                    "type": "string",
                                    "description": "First choice in German (Ich... form)"
                                },
                                "choice_2": {
                                    "type": "string",
                                    "description": "Second choice in German (Ich... form)"
                                },
                                "choice_3": {
                                    "type": "string",
                                    "description": "Third choice in German (Ich... form)"
                                },
                                "characters_in_scene": {
                                    "type": "array",
                                    "description": "Characters visible in the scene",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "Character name"
                                            },
                                            "description": {
                                                "type": "string",
                                                "description": "Visual description (for new characters only)"
                                            }
                                        },
                                        "required": ["name"],
                                        "additionalProperties": False
                                    }
                                }
                            },
                            "required": ["story_text", "image_prompt", "choice_1", "choice_2", "choice_3", "characters_in_scene"],
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
        # DEV MODE: Skip image generation and return placeholder
        if settings.dev_mode:
            logger.info("🚧 [DEV MODE] Skipping image generation, returning placeholder")
            return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='600'%3E%3Crect width='800' height='600' fill='%23e0f2fe'/%3E%3Ctext x='50%25' y='45%25' text-anchor='middle' fill='%230369a1' font-size='32' font-weight='bold'%3EM%C3%A4rchenweber%3C/text%3E%3Ctext x='50%25' y='55%25' text-anchor='middle' fill='%2306b6d4' font-size='20'%3EDEV MODE%3C/text%3E%3C/svg%3E"

        # Build the content array for multimodal input
        # OpenRouter docs: send text first, then images to avoid parsing issues
        content = []

        # Add style instructions if provided
        if style_description:
            enhanced_prompt = f"Continue in the same art style: {style_description}\n\n{prompt}"
        else:
            enhanced_prompt = prompt

        # Add text prompt first (recommended by OpenRouter)
        content.append({
            "type": "text",
            "text": enhanced_prompt
        })

        # Add previous image if provided (for style consistency)
        # Only add if it's a valid URL (not empty)
        if previous_image_url and len(previous_image_url) > 0:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": previous_image_url
                }
            })
            logger.info(f"Including previous image for style consistency (type: {'data URL' if previous_image_url.startswith('data:') else 'hosted URL'})")

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": aspect_ratio},
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                logger.info(f"🌐 [API CALL] Calling OpenRouter image generation API...")
                logger.info(f"  - Model: {model}")
                logger.info(f"  - Prompt length: {len(prompt)} chars")
                logger.info(f"  - Aspect ratio: {aspect_ratio}")
                logger.info(f"  - Timeout: 120s")

                response = await client.post(
                    OPENROUTER_API_URL,
                    headers=self.headers,
                    json=payload,
                )

                logger.info(f"📥 [API RESPONSE] Status: {response.status_code}")

                if response.status_code != 200:
                    logger.error(f"❌ [API ERROR] Non-200 status code: {response.status_code}")
                    logger.error(f"  - Response text: {response.text[:1000]}")

                response.raise_for_status()
                result = response.json()

                logger.info(f"📦 [API RESPONSE] Response keys: {list(result.keys())}")

                # Check for API errors in response
                if "error" in result:
                    logger.error(f"❌ [API ERROR] Error in response: {result['error']}")
                    raise ValueError(f"OpenRouter API error: {result['error']}")

                # Extract image URL from response
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0]["message"]
                    logger.info(f"📦 [API RESPONSE] Message keys: {list(message.keys())}")

                    # Check for images in the response
                    if "images" in message and len(message["images"]) > 0:
                        image_data = message["images"][0]
                        image_url = image_data["image_url"]["url"]
                        url_type = "data URL" if image_url.startswith("data:") else "hosted URL"
                        url_preview = image_url[:100] if len(image_url) > 100 else image_url
                        logger.info(f"✅ [API RESPONSE] Image URL received ({url_type}): {url_preview}...")
                        return image_url
                    else:
                        logger.warning("⚠️ [API RESPONSE] No images in API response, returning placeholder")
                        logger.warning(f"  - Message content: {message}")
                        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='600'%3E%3Crect width='800' height='600' fill='%23f3f4f6'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' fill='%236b7280' font-size='24'%3EMärchenweber%3C/text%3E%3C/svg%3E"
                else:
                    logger.error(f"❌ [API RESPONSE] No choices in API response")
                    logger.error(f"  - Full response: {result}")
                    raise ValueError("No choices in API response")

            except httpx.TimeoutException as e:
                logger.error(f"❌ [API TIMEOUT] Image generation timed out after 120s")
                logger.error(f"  - Model: {model}")
                logger.error(f"  - This may indicate the model is slow, unavailable, or doesn't support image generation")
                raise ValueError(f"Image generation timed out. Model '{model}' may not support image generation or is overloaded.")
            except httpx.HTTPError as e:
                logger.error(f"❌ [API ERROR] OpenRouter image generation error: {e}")
                if 'response' in locals():
                    logger.error(f"Response status: {response.status_code}")
                    logger.error(f"Response text: {response.text[:500]}")
                # Return placeholder image on error
                return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='600'%3E%3Crect width='800' height='600' fill='%23f3f4f6'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' fill='%236b7280' font-size='24'%3EMärchenweber%3C/text%3E%3C/svg%3E"
            except (KeyError, IndexError, ValueError) as e:
                logger.error(f"Failed to parse image API response: {e}")
                if 'result' in locals():
                    logger.error(f"API response structure: {result}")
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
