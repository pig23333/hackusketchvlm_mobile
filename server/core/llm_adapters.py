"""
LLM Adapters - Unified interface for multimodal Vision-Language Models.
Supports OpenRouter, OpenAI, and Anthropic backends with automatic message normalization.
All comments and documentation are in English.
"""

import os
import re
import base64
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class BaseLLMAdapter:
    """Base interface for all LLM providers."""

    def __init__(self, model: str, cache: bool = False, max_tokens: int = 2048):
        self.model = model
        self.cache = cache
        self.max_tokens = max_tokens

    def call(self, system_message: str, messages: List[Dict], additional_args: Optional[Dict] = None):
        raise NotImplementedError

    def extract_text(self, raw_response) -> str:
        raise NotImplementedError


class OpenRouterAdapter(BaseLLMAdapter):
    """
    Adapter for OpenRouter API (gateway for Qwen, GPT-4o, Claude, etc.).
    Normalizes both Anthropic-style and OpenAI-style image payloads.
    """

    def __init__(self, model: str, cache: bool = False, max_tokens: int = 2048):
        super().__init__(model, cache, max_tokens)
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set.")

        from openai import OpenAI
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/pig23333/hackusketchvlm_mobile",
                "X-Title": "SketchVLM Mobile Video Backend"
            }
        )

    def _normalize_chat_messages(self, messages: List[Dict]) -> List[Dict]:
        """Convert any Anthropic image format to standard OpenAI image_url format."""
        normalized = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content")

            if isinstance(content, list):
                new_parts = []
                for part in content:
                    ptype = part.get("type")
                    if ptype == "image":
                        src = part.get("source", {})
                        if src.get("type") == "base64":
                            media_type = src.get("media_type", "image/png")
                            b64_data = src.get("data", "")
                            new_parts.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:{media_type};base64,{b64_data}"}
                            })
                        else:
                            new_parts.append(part)
                    else:
                        new_parts.append(part)
                normalized.append({"role": role, "content": new_parts})
            else:
                normalized.append(msg)
        return normalized

    def call(self, system_message: str, messages: List[Dict], additional_args: Optional[Dict] = None):
        add_args = additional_args or {}
        chat_messages = self._normalize_chat_messages(messages)

        if isinstance(system_message, str) and system_message.strip():
            chat_messages = [{"role": "system", "content": system_message}] + chat_messages

        params = {
            "model": self.model,
            "messages": chat_messages,
            "max_tokens": self.max_tokens,
        }
        if "temperature" in add_args:
            params["temperature"] = float(add_args["temperature"])

        return self._client.chat.completions.create(**params)

    def extract_text(self, raw_response) -> str:
        if hasattr(raw_response, "choices") and raw_response.choices:
            return raw_response.choices[0].message.content or ""
        return ""


class OpenAIAdapter(BaseLLMAdapter):
    """Direct OpenAI API adapter (GPT-4o, GPT-4o-mini)."""

    def __init__(self, model: str, cache: bool = False, max_tokens: int = 2048):
        super().__init__(model, cache, max_tokens)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        from openai import OpenAI
        self._client = OpenAI(api_key=api_key)

    def call(self, system_message: str, messages: List[Dict], additional_args: Optional[Dict] = None):
        add_args = additional_args or {}
        chat_messages = list(messages)
        if system_message:
            chat_messages = [{"role": "system", "content": system_message}] + chat_messages

        params = {
            "model": self.model,
            "messages": chat_messages,
            "max_tokens": self.max_tokens,
        }
        if "temperature" in add_args:
            params["temperature"] = float(add_args["temperature"])

        return self._client.chat.completions.create(**params)

    def extract_text(self, raw_response) -> str:
        if hasattr(raw_response, "choices") and raw_response.choices:
            return raw_response.choices[0].message.content or ""
        return ""


def make_adapter(provider: str, model: str, cache: bool = False, max_tokens: int = 2048) -> BaseLLMAdapter:
    """Factory function for instantiating model adapters."""
    prov = (provider or "").strip().lower()
    if prov in ("openrouter", "or"):
        return OpenRouterAdapter(model=model, cache=cache, max_tokens=max_tokens)
    elif prov == "openai":
        return OpenAIAdapter(model=model, cache=cache, max_tokens=max_tokens)
    else:
        # Default to OpenRouter for maximum model flexibility
        return OpenRouterAdapter(model=model, cache=cache, max_tokens=max_tokens)
