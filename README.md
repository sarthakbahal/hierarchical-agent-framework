# Hierarchical Agent Framework

A modular and extensible framework for building multi-agent AI systems with hierarchical task coordination. This framework enables complex task execution through specialized agents that work together under intelligent orchestration.

## Overview

The Hierarchical Agent Framework implements a multi-agent architecture where specialized agents collaborate to solve complex problems. An orchestrator agent analyzes tasks, delegates to appropriate specialized agents (planner, coder, etc.), and synthesizes results into coherent outcomes.

### Key Features

- **Hierarchical Coordination**: Orchestrator agent manages and delegates tasks to specialized agents
- **Specialized Agents**: Purpose-built agents for planning, coding, and task execution
- **Tool Integration**: Extensible tool system for file operations, code execution, and web search
- **Async Architecture**: Built on Python asyncio for efficient concurrent operations
- **LLM Provider Flexibility**: Support for multiple LLM providers (Groq, OpenAI, Anthropic, Ollama)
- **Robust Configuration**: Pydantic-based settings management with environment variable support
- **Comprehensive Logging**: Structured logging for debugging and monitoring

## Architecture

```
User Task
    ↓
OrchestratorAgent (Coordinator)
    ↓
    ├─→ PlannerAgent (Strategic Planning)
    ├─→ CoderAgent (Code Implementation)
    └─→ [Future Agents...]
         ↓
    Tool System
    ├─→ File Operations (read, write, list)
    ├─→ Code Execution
    └─→ Web Search
```

### Agent Types

- **OrchestratorAgent**: Coordinates multiple agents, decomposes complex tasks, and synthesizes results
- **PlannerAgent**: Creates detailed execution plans and architectural designs
- **CoderAgent**: Writes, modifies, and manages code with best practices

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- API key for your chosen LLM provider (Groq, OpenAI, etc.)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/hierarchical-agent-framework.git
cd hierarchical-agent-framework
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```env
# LLM Provider Configuration
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-70b-versatile

# API Keys (use only what you need)
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Logging Configuration
LOG_LEVEL=INFO
```

#### Supported LLM Providers

- **Groq**: Fast inference with Llama and Mixtral models
  - Models: `llama-3.1-70b-versatile`, `mixtral-8x7b-32768`
- **OpenAI**: GPT models
  - Models: `gpt-4-turbo-preview`, `gpt-3.5-turbo`
- **Anthropic**: Claude models
  - Models: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- **Ollama**: Local model deployment
  - Requires local Ollama installation

## Usage

### Basic Usage

Run individual agents directly:

```bash
python examples/basic_usage.py
```

This example demonstrates:
- Using the PlannerAgent to create task execution plans
- Using the CoderAgent to write code
- File operations through agent tools

### Advanced Orchestration

Run complex multi-agent coordination:

```bash
python examples/advanced_orchestration.py
```

This example demonstrates:
- Task decomposition and delegation
- Multi-agent coordination
- Sequential and parallel agent execution
- Result synthesis


## Project Structure

```
hierarchical-agent-framework/
├── src/
│   ├── agents/           # Agent implementations
│   │   ├── orchestrator.py   # Main coordinator agent
│   │   ├── planner.py        # Planning specialist
│   │   └── coder.py          # Coding specialist
│   ├── core/             # Core framework components
│   │   ├── base_agent.py     # Abstract agent base class
│   │   ├── base_tool.py      # Tool interface
│   │   └── llm_client.py     # LLM provider abstraction
│   ├── tools/            # Tool implementations
│   │   ├── file_read.py      # File reading
│   │   ├── file_write.py     # File writing
│   │   ├── list_directory.py # Directory listing
│   │   ├── code_execute.py   # Code execution
│   │   └── web_search.py     # Web search capability
│   └── utils/            # Utilities
│       ├── config.py         # Configuration management
│       └── logger.py         # Logging setup
├── examples/             # Usage examples
│   ├── basic_usage.py        # Basic agent usage
│   └── advanced_orchestration.py  # Multi-agent coordination
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Configuration

The framework uses Pydantic for configuration management. All settings can be configured via environment variables or the `.env` file.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes with clear commit messages
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Built with async Python for efficient concurrent operations
- Uses Pydantic for robust configuration management
- Supports multiple LLM providers for flexibility

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.
