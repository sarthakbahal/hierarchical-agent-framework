"""
FileReadTool - Your first real tool implementation!

YOUR TASK: Complete the FileReadTool class

WHAT YOU'LL DO:
1. Import the necessary modules (I'll guide you)
2. Fill in the property return values
3. Implement the execute method (with my help)

This is easier than BaseTool because you're implementing, not designing!
"""

import aiofiles  # For async file operations
from src.core.base_tool import BaseTool  # Import our abstract base class


class FileReadTool(BaseTool):
    """
    A tool that reads the contents of a file asynchronously.
    
    This tool allows agents to read files from the filesystem.
    """
    
    # ========================================================================
    # PROPERTY 1: Fill in the name
    # ========================================================================
    
    @property
    def name(self) -> str:
        """Return the name of this tool."""
        return "file_read"
    
    
    # ========================================================================
    # PROPERTY 2: Fill in the description
    # ========================================================================
    
    @property
    def description(self) -> str:
        """Return a description of what this tool does."""
        return "Reads the contents of a file from the filesystem"
    
    
    # ========================================================================
    # PROPERTY 3: Fill in the parameters (I'll help more here)
    # ========================================================================
    
    @property
    def parameters(self) -> dict:
        """
        Define what parameters this tool needs.
        
        FileReadTool needs ONE parameter: file_path (a string)
        """
        # TODO: Return this dictionary (you can copy-paste this one):
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to read"
                }
            },
            "required": ["file_path"]  # file_path is mandatory
        }
    
    
    # ========================================================================
    # METHOD: execute - The actual file reading logic
    # ========================================================================
    
    async def execute(self, params: dict) -> str:
        """
        Read a file and return its contents.
        
        Args:
            params: Dictionary with "file_path" key
            
        Returns:
            str: The contents of the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: For other errors
        """
        # Step 1: Get the file_path from params
        file_path = params.get("file_path")
        
        # Step 2: Validate that file_path was provided
        if not file_path:
            raise ValueError("file_path parameter is required")
        
        # Step 3: Read the file asynchronously (I'll give you this part)
        try:
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
                contents = await file.read()
                return contents
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")


# ============================================================================
# YOUR LEARNING QUESTIONS - Answer these!
# ============================================================================

# Q1: Why do we use 'aiofiles' instead of regular 'open()'?
# A1: 

# Q2: What does 'async with' mean?
# A2: 

# Q3: Why does execute() return 'str' but BaseTool.execute returns 'Any'?
# A3: 

# Q4: What happens if someone calls this tool without a file_path?
# A4: 
