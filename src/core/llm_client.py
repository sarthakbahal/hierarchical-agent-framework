"""
LLMClient - Unified interface for multiple LLM providers

LEARNING POINTS:
- Abstraction pattern: Hide provider-specific details
- Async HTTP communication with LLMs
- Error handling and retries
- Message formatting for different providers
- Function/tool calling support
- Easy to swap providers without changing agent code

Why abstract the LLM?
- Agents don't care which LLM they use
- Easy to switch from Groq → OpenAI → Anthropic
- Centralized error handling
- Consistent interface across providers
- Can add features (caching, retries) in one place
"""

import aiohttp
import json
from typing import List, Dict, Optional, Any
from src.utils.config import settings
from src.utils.logger import setup_logger


class LLMClient:
    """
    Universal client for interacting with different LLM providers.
    
    Supported providers:
    - Groq (FREE - recommended for learning)
    - OpenAI (paid, best quality)
    - Anthropic (paid, great reasoning)
    - Ollama (FREE, local)
    
    Usage:
        client = LLMClient()
        response = await client.generate(
            messages=[{"role": "user", "content": "Hello!"}],
            system_prompt="You are a helpful assistant"
        )
    """
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            provider: Which provider to use (overrides config)
            model: Which model to use (overrides config)
        """
        self.provider = provider or settings.llm_provider
        self.model = model or settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.logger = setup_logger(f"LLMClient.{self.provider}")
        
        # Validate provider and API key
        self._validate_configuration()
    
    def _validate_configuration(self):
        """
        Ensure we have the necessary API keys for the chosen provider.
        
        Why validate?
        - Fail fast if configuration is wrong
        - Clear error messages
        - Prevents runtime errors later
        """
        if self.provider == "groq" and not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        elif self.provider == "openai" and not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        elif self.provider == "anthropic" and not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")
        elif self.provider == "ollama":
            # Ollama is local, no API key needed
            pass
        else:
            if self.provider not in ["groq", "openai", "anthropic", "ollama"]:
                raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.
        
        This is the main method agents will use.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
                     Example: [{"role": "user", "content": "Hello!"}]
            system_prompt: Optional system message defining agent behavior
            tools: Optional list of tool definitions for function calling
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict with:
            - content: The LLM's text response
            - tool_calls: List of tool calls (if any)
            - finish_reason: Why generation stopped
            - usage: Token usage statistics
        """
        self.logger.debug(f"Generating response with {len(messages)} messages")
        
        try:
            # Route to correct provider
            if self.provider == "groq":
                return await self._generate_groq(messages, system_prompt, tools, **kwargs)
            elif self.provider == "openai":
                return await self._generate_openai(messages, system_prompt, tools, **kwargs)
            elif self.provider == "anthropic":
                return await self._generate_anthropic(messages, system_prompt, tools, **kwargs)
            elif self.provider == "ollama":
                return await self._generate_ollama(messages, system_prompt, tools, **kwargs)
            else:
                raise ValueError(f"Provider {self.provider} not implemented")
                
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def _generate_groq(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
        tools: Optional[List[Dict]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response using Groq API.
        
        Groq uses OpenAI-compatible API, so the format is similar.
        
        API Docs: https://console.groq.com/docs
        """
        # Prepare messages with system prompt if provided
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)
        
        # Build request payload
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        # Add tools if provided (function calling)
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"  # Let model decide when to use tools
        
        # Make API request
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Groq API error ({response.status}): {error_text}")
                
                result = await response.json()
        
        # Parse response
        message = result["choices"][0]["message"]
        
        return {
            "content": message.get("content", ""),
            "tool_calls": message.get("tool_calls", []),
            "finish_reason": result["choices"][0]["finish_reason"],
            "usage": result.get("usage", {})
        }
    
    async def _generate_openai(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
        tools: Optional[List[Dict]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response using OpenAI API.
        
        Very similar to Groq since Groq uses OpenAI-compatible format.
        
        API Docs: https://platform.openai.com/docs/api-reference
        """
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error ({response.status}): {error_text}")
                
                result = await response.json()
        
        message = result["choices"][0]["message"]
        
        return {
            "content": message.get("content", ""),
            "tool_calls": message.get("tool_calls", []),
            "finish_reason": result["choices"][0]["finish_reason"],
            "usage": result.get("usage", {})
        }
    
    async def _generate_anthropic(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
        tools: Optional[List[Dict]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response using Anthropic API (Claude).
        
        Anthropic uses different format than OpenAI:
        - system is a separate parameter, not in messages
        - Different tool calling format
        
        API Docs: https://docs.anthropic.com/claude/reference/
        """
        payload = {
            "model": self.model,
            "messages": messages,  # No system message in messages list
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
        }
        
        # System prompt is separate in Anthropic API
        if system_prompt:
            payload["system"] = system_prompt
        
        # Anthropic tool format is slightly different
        if tools:
            payload["tools"] = tools
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error ({response.status}): {error_text}")
                
                result = await response.json()
        
        # Parse Anthropic's response format
        content = ""
        tool_calls = []
        
        for block in result.get("content", []):
            if block["type"] == "text":
                content += block["text"]
            elif block["type"] == "tool_use":
                tool_calls.append(block)
        
        return {
            "content": content,
            "tool_calls": tool_calls,
            "finish_reason": result.get("stop_reason", ""),
            "usage": result.get("usage", {})
        }
    
    async def _generate_ollama(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
        tools: Optional[List[Dict]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response using Ollama (local models).
        
        Ollama runs models locally - no API key needed!
        
        API Docs: https://github.com/ollama/ollama/blob/main/docs/api.md
        """
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": False,  # Don't stream for simplicity
            "options": {
                "temperature": kwargs.get("temperature", self.temperature),
                "num_predict": kwargs.get("max_tokens", self.max_tokens),
            }
        }
        
        # Ollama's tool support is limited - skip for now
        if tools:
            self.logger.warning("Ollama tool calling support is limited")
        
        url = f"{settings.ollama_base_url}/api/chat"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error ({response.status}): {error_text}")
                
                result = await response.json()
        
        return {
            "content": result["message"]["content"],
            "tool_calls": [],  # Ollama doesn't support tool calling yet
            "finish_reason": "stop",
            "usage": {
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0),
            }
        }


# LEARNING QUESTIONS:
# Q1: Why have one generate() method that routes to provider-specific methods?
# A1: Single interface for agents - they call generate() regardless of provider
#     Makes switching providers easy - just change config
#     Keeps provider-specific logic isolated

# Q2: Why make API calls async?
# A2: LLM APIs can take seconds to respond (I/O wait time)
#     Async allows other operations to continue
#     Essential for responsive multi-agent systems

# Q3: Why return a dict instead of just the content string?
# A3: Agents need more than just text:
#     - Tool calls (function calling)
#     - Usage stats (for cost tracking)
#     - Finish reason (did it hit token limit?)
#     Rich data enables better agent behavior

# Q4: How would you add retry logic?
# A4: Wrap the API call in a retry loop:
#     for attempt in range(max_retries):
#         try:
#             return await make_api_call()
#         except Exception:
#             if attempt == max_retries - 1:
#                 raise
#             await asyncio.sleep(backoff_time)
