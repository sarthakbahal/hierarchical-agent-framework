"""
CoderAgent - Writes and modifies code

LEARNING POINTS:
- Tool-heavy agent (uses file tools extensively)
- Specialized for code generation
- Can read existing code, write new code
- Follows best practices and patterns

Role:
- Implements code based on specifications
- Reads and understands existing code
- Writes clean, documented code
- Follows coding standards
"""

from src.core.base_agent import BaseAgent
from src.core.llm_client import LLMClient
from src.tools.file_read import FileReadTool
from src.tools.file_write import FileWriteTool
from src.tools.list_directory import ListDirectoryTool
from typing import Optional, List
from src.core.base_tool import BaseTool


class CoderAgent(BaseAgent):
    """
    Agent specialized in writing and modifying code.
    
    Think of this as a Senior Developer:
    - Implements features from specifications
    - Reads and understands existing code
    - Writes clean, maintainable code
    - Follows best practices
    - Documents code properly
    
    When to use:
    - Implementing new features
    - Refactoring existing code
    - Fixing bugs
    - Creating new files/modules
    """
    
    def __init__(
        self,
        tools: Optional[List[BaseTool]] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize the Coder Agent.
        
        By default, provide file manipulation tools.
        Can add more tools (code execution, linting, etc.)
        """
        # Default tools for coding tasks
        default_tools = [
            FileReadTool(),
            FileWriteTool(),
            ListDirectoryTool()
        ]
        
        # Merge with any additional tools provided
        all_tools = default_tools + (tools or [])
        
        super().__init__(
            name="CoderAgent",
            tools=all_tools,
            llm_client=llm_client
        )
    
    @property
    def system_prompt(self) -> str:
        """
        Define the Coder's role and expertise.
        
        Key aspects:
        - Expert programmer
        - Follows best practices
        - Writes clean, documented code
        - Uses tools to interact with filesystem
        """
        return """You are an expert Senior Software Developer with deep knowledge of multiple programming languages and best practices.

Your role is to write high-quality, production-ready code.

When implementing code, you should:
1. Read and understand existing code if modifying
2. Follow established patterns and conventions
3. Write clean, readable, well-documented code
4. Include docstrings and comments where helpful
5. Handle errors appropriately
6. Use tools to read/write files as needed

You have access to these tools:
- **file_read**: Read contents of files
- **file_write**: Write or modify files
- **list_directory**: List files in a directory

Best practices you follow:
- Clear variable and function names
- Single Responsibility Principle
- DRY (Don't Repeat Yourself)
- Proper error handling
- Type hints (for Python)
- Comprehensive docstrings
- Comments for complex logic only

When given a task:
1. Use list_directory to understand project structure
2. Use file_read to understand existing code
3. Implement the feature following best practices
4. Use file_write to create/modify files
5. Explain what you did and why

Always explain your implementation decisions briefly."""
    
    async def write_code(
        self,
        task: str,
        file_path: Optional[str] = None,
        existing_code: Optional[str] = None
    ) -> str:
        """
        Write or modify code based on task description.
        
        Convenience method with clearer name and additional context.
        
        Args:
            task: What code to write (feature, fix, etc.)
            file_path: Optional file path for context
            existing_code: Optional existing code to modify
            
        Returns:
            Result message describing what was done
        """
        context = {}
        if file_path:
            context["file_path"] = file_path
        if existing_code:
            context["existing_code"] = existing_code
        
        return await self.execute(task, context)


# LEARNING QUESTIONS:
# Q1: Why give CoderAgent default tools in __init__?
# A1: Coders always need file tools - it's part of their role
#     Convenience - don't have to specify tools every time
#     Can still add more tools if needed (flexibility)

# Q2: Why include best practices in system prompt?
# A2: Guides the LLM to write better code
#     Sets expectations for code quality
#     Reduces need for code review/fixes
#     Makes output more predictable

# Q3: Why create write_code() method?
# A3: More intuitive API - coder.write_code() is clearer than execute()
#     Allows adding context parameters specific to coding
#     Could add more methods (refactor_code, fix_bug, etc.)

# Q4: How could you improve code quality validation?
# A4: Add tools for:
#     - Syntax checking (AST parsing)
#     - Linting (pylint, flake8)
#     - Type checking (mypy)
#     - Running tests
#     - Code formatting (black)
#     Agent could validate before writing files
