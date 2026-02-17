"""
Configuration Management

LEARNING POINTS:
- Uses pydantic for settings validation
- Loads from .env file automatically
- Type-safe configuration access
- Default values for optional settings
- Validates required settings on startup

Why pydantic?
- Automatic validation (catches config errors early)
- Type conversion (string "30" → int 30)
- Environment variable loading
- IDE autocomplete for settings
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    
    How it works:
    1. Pydantic reads .env file
    2. Validates all required fields exist
    3. Converts types automatically
    4. Provides defaults for optional fields
    5. Raises error if validation fails
    
    Usage:
        settings = Settings()  # Loads from .env
        print(settings.llm_provider)  # Access typed value
    """
    
    # ========================================================================
    # LLM CONFIGURATION
    # ========================================================================
    
    llm_provider: str = "groq"
    """Which LLM provider to use (groq, openai, anthropic, ollama)"""
    
    llm_model: str = "llama-3.1-70b-versatile"
    """
    Which model to use (depends on provider):
    - Groq: llama-3.1-70b-versatile, mixtral-8x7b-32768
    - OpenAI: gpt-4-turbo-preview, gpt-3.5-turbo
    - Anthropic: claude-3-opus-20240229, claude-3-sonnet-20240229
    - Ollama: llama3, mistral, codellama
    """
    
    llm_temperature: float = 0.7
    """
    Temperature for LLM sampling (0.0 to 2.0)
    - 0.0: Deterministic, focused responses
    - 1.0: Balanced creativity and coherence
    - 2.0: Maximum creativity, less focused
    """
    
    llm_max_tokens: int = 4000
    """Maximum tokens in LLM response"""
    
    # ========================================================================
    # API KEYS (Required for cloud providers)
    # ========================================================================
    
    groq_api_key: Optional[str] = None
    """Groq API key (get from https://console.groq.com)"""
    
    openai_api_key: Optional[str] = None
    """OpenAI API key (get from https://platform.openai.com)"""
    
    anthropic_api_key: Optional[str] = None
    """Anthropic API key (get from https://console.anthropic.com)"""
    
    ollama_base_url: str = "http://localhost:11434"
    """Ollama server URL (for local models)"""
    
    # ========================================================================
    # TOOL CONFIGURATION
    # ========================================================================
    
    code_execute_timeout: int = 30
    """Maximum seconds for code execution (prevents infinite loops)"""
    
    web_search_max_results: int = 5
    """Maximum number of web search results to return"""
    
    # ========================================================================
    # AGENT CONFIGURATION
    # ========================================================================
    
    max_agent_iterations: int = 10
    """Maximum iterations for an agent to solve a task (prevents loops)"""
    
    agent_timeout: int = 300
    """Maximum seconds for an agent to complete a task"""
    
    # ========================================================================
    # PYDANTIC CONFIGURATION
    # ========================================================================
    
    class Config:
        """
        Pydantic configuration.
        
        env_file: Path to .env file
        env_file_encoding: Character encoding for .env
        case_sensitive: Environment variables are case-insensitive
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Singleton instance - load once and reuse
# This ensures all parts of the app use the same configuration
try:
    settings = Settings()
except Exception as e:
    print(f"❌ Error loading configuration from .env file:")
    print(f"   {str(e)}")
    print("\nMake sure you:")
    print("1. Created .env file (copy from .env.example)")
    print("2. Added your API key(s)")
    print("3. Set LLM_PROVIDER to match your API key")
    raise


# LEARNING QUESTIONS:
# Q1: Why use pydantic instead of just os.getenv()?
# A1: Pydantic provides:
#     - Automatic type conversion and validation
#     - Default values
#     - Better error messages
#     - IDE autocomplete
#     - Single source of truth for all settings

# Q2: What does Optional[str] mean?
# A2: The value can be either a string or None
#     Allows settings to be optional (like API keys you don't use)

# Q3: Why make settings a singleton?
# A3: Configuration should be loaded once at startup
#     All parts of the app share the same config
#     Avoids re-reading .env file repeatedly

# Q4: What happens if required field is missing?
# A4: Pydantic raises ValidationError with clear message
#     about which field is missing - fails fast!
