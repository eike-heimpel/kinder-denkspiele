"""Configuration loader with YAML and Jinja2 template support."""

import random
from pathlib import Path
from typing import Any, Dict
import yaml
from jinja2 import Template


class ConfigLoader:
    """Load and manage configuration from YAML file with Jinja2 templating."""

    def __init__(self, config_path: str | None = None):
        """Initialize the config loader.

        Args:
            config_path: Path to config.yaml file. If None, uses default location.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config.yaml"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self._config: Dict[str, Any] = yaml.safe_load(f)

    def get_model(self, model_name: str) -> str:
        """Get model identifier by name.

        Args:
            model_name: Name of the model (e.g., 'narrator', 'validator')

        Returns:
            Model identifier string for OpenRouter API
        """
        models = self._config.get("models", {})
        if model_name not in models:
            raise ValueError(f"Model '{model_name}' not found in config")
        return models[model_name]

    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """Get and render a prompt template with Jinja2.

        Args:
            prompt_name: Name of the prompt (e.g., 'narrator', 'validator')
            **kwargs: Variables to inject into the template

        Returns:
            Rendered prompt string
        """
        prompts = self._config.get("prompts", {})

        # Handle nested prompts (e.g., choice_prompts.brave)
        if "." in prompt_name:
            parts = prompt_name.split(".")
            prompt_data = prompts
            for part in parts:
                prompt_data = prompt_data.get(part, {})
            template_str = prompt_data
        else:
            template_str = prompts.get(prompt_name)

        if not template_str:
            raise ValueError(f"Prompt '{prompt_name}' not found in config")

        template = Template(template_str)
        return template.render(**kwargs)

    def get_random_wildcard(self) -> str:
        """Get a random wildcard element to inject into the story.

        Returns:
            Random wildcard string
        """
        wildcards = self._config.get("wildcards", [])
        if not wildcards:
            raise ValueError("No wildcards found in config")
        return random.choice(wildcards)

    def get_sampling_params(self, agent_name: str) -> Dict[str, Any]:
        """Get sampling parameters for a specific agent.

        Args:
            agent_name: Name of the agent (e.g., 'narrator', 'choice_agent_brave')

        Returns:
            Dictionary of sampling parameters
        """
        sampling_params = self._config.get("sampling_params", {})
        return sampling_params.get(agent_name, {})

    def get_game_mechanic(self, mechanic_name: str, default: Any = None) -> Any:
        """Get a game mechanic configuration value.

        Args:
            mechanic_name: Name of the mechanic (e.g., 'image_generation_interval')
            default: Default value if not found

        Returns:
            Mechanic value or default
        """
        game_mechanics = self._config.get("game_mechanics", {})
        return game_mechanics.get(mechanic_name, default)

    def get_config(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary.

        Returns:
            Complete config dictionary
        """
        return self._config


# Global config loader instance
_config_loader: ConfigLoader | None = None


def get_config_loader() -> ConfigLoader:
    """Get or create the global config loader instance.

    Returns:
        ConfigLoader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader
