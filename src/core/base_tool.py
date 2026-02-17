"""
BaseTool - Abstract base class for all tools

This file demonstrates core Python concepts:
1. Abstract Base Classes (ABC) - for defining interfaces
2. Type hints - for code clarity and IDE support
3. Async methods - for non-blocking operations
4. Property decorators - for defining getters

READ CAREFULLY: Every line has an explanation!
"""

# ============================================================================
# IMPORTS - What we need from Python's standard library
# ============================================================================

from abc import ABC, abstractmethod  
# ABC = Abstract Base Class - prevents direct instantiation
# abstractmethod = decorator to mark methods that MUST be implemented by subclasses

from typing import Any, Dict
# Any = means "any type" - flexible return type
# Dict = dictionary type hint (like {"key": "value"})


# ============================================================================
# BASE TOOL CLASS - The foundation for all tools
# ============================================================================

class BaseTool(ABC):
    """
    Abstract base class for all tools that agents can use.
    
    Why abstract? 
    - We want a blueprint/contract that all tools must follow
    - We don't want anyone creating a "BaseTool" directly
    - Every real tool (like FileReadTool) must inherit from this
    
    Every tool must implement:
    - name: Unique identifier for the tool
    - description: What the tool does (LLM reads this!)
    - parameters: JSON schema of expected inputs
    - execute: Async method that performs the tool's action
    """
    
    # ========================================================================
    # PROPERTY 1: name
    # ========================================================================
    
    @property              # Makes this a property (accessed like: tool.name)
    @abstractmethod        # Forces subclasses to implement this
    def name(self) -> str: # Type hint: this returns a string
        """
        Unique identifier for this tool.
        
        Example: "file_read", "web_search", "code_execute"
        
        Why a property? So each tool can define its own name.
        Why abstract? Every tool MUST have a name.
        """
        pass  # Empty body - subclasses provide the real implementation
    
    
    # ========================================================================
    # PROPERTY 2: description
    # ========================================================================
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Human-readable description of what this tool does.
        
        This is shown to the LLM so it knows when to use this tool!
        
        Example: "Reads the contents of a file from the filesystem"
        """
        pass
    
    
    # ========================================================================
    # PROPERTY 3: parameters
    # ========================================================================
    
    @property
    @abstractmethod
    def parameters(self) -> Dict:
        """
        JSON Schema describing the parameters this tool accepts.
        
        Why JSON Schema? It's a standard way to describe data structure.
        The LLM uses this to know what arguments to pass!
        
        Example for a file_read tool:
        {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["file_path"]
        }
        """
        pass
    
    
    # ========================================================================
    # METHOD: execute (ASYNC!)
    # ========================================================================
    
    @abstractmethod
    async def execute(self, params: Dict) -> Any:
        """
        Execute the tool's action asynchronously.
        
        Why async? Tools often do I/O operations:
        - Reading files (disk I/O)
        - Web requests (network I/O)
        - Database queries (network I/O)
        
        Async allows other operations to continue while waiting!
        
        Args:
            params (Dict): The parameters for this tool execution
                          Example: {"file_path": "/path/to/file.txt"}
        
        Returns:
            Any: The result of the tool execution
                 Different tools return different types:
                 - file_read might return str (file contents)
                 - web_search might return list (search results)
                 - code_execute might return dict (output + errors)
        """
        pass


# ============================================================================
# UNDERSTANDING CHECK - Answer these questions!
# ============================================================================

# Q1: Why do we use ABC (Abstract Base Class)?
# A1: To create a blueprint/contract that all tools must follow. It prevents
#     creating BaseTool directly and forces subclasses to implement all
#     abstract methods and properties. This ensures consistency.

# Q2: Why is execute() async instead of sync?
# A2: Because tools often perform I/O operations (reading files, web requests)
#     which can be slow. Async allows the program to do other work while
#     waiting, making the system more efficient and responsive.

# Q3: What happens if someone tries to instantiate BaseTool directly?
# A3: Python raises a TypeError saying "Can't instantiate abstract class
#     BaseTool with abstract methods..." because ABC prevents instantiation
#     of classes with unimplemented abstract methods.

# Q4: What happens if a subclass doesn't implement all abstract methods?
# A4: Same as Q3 - you get a TypeError when trying to create an instance.
#     The subclass remains abstract until ALL abstract methods/properties
#     are implemented. 
