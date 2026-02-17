"""
FileWriteTool - Writes content to files

LEARNING POINTS:
- Similar structure to FileReadTool but with write operations
- Handles both creating new files and overwriting existing ones
- Uses 'w' mode for writing (overwrites) vs 'a' mode (appends)
- Error handling for write permissions
"""

import aiofiles
from pathlib import Path
from src.core.base_tool import BaseTool


class FileWriteTool(BaseTool):
    """
    A tool that writes content to a file asynchronously.
    
    Why async for writing?
    - Disk I/O can be slow, especially for large files
    - Async allows other operations to continue while writing
    - Essential for responsive agent systems
    """
    
    @property
    def name(self) -> str:
        """Unique identifier for this tool."""
        return "file_write"
    
    @property
    def description(self) -> str:
        """Description for LLM to understand when to use this tool."""
        return "Writes content to a file, creating it if it doesn't exist or overwriting if it does"
    
    @property
    def parameters(self) -> dict:
        """
        This tool needs TWO parameters:
        1. file_path: Where to write
        2. content: What to write
        """
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                }
            },
            "required": ["file_path", "content"]  # Both are mandatory
        }
    
    async def execute(self, params: dict) -> str:
        """
        Write content to a file.
        
        Process:
        1. Extract and validate parameters
        2. Ensure parent directory exists
        3. Write content asynchronously
        4. Return success message
        
        Args:
            params: Dict with "file_path" and "content"
            
        Returns:
            str: Success message with number of bytes written
        """
        # Validate parameters
        file_path = params.get("file_path")
        content = params.get("content")
        
        if not file_path:
            raise ValueError("file_path parameter is required")
        if content is None:  # Allow empty string but not None
            raise ValueError("content parameter is required")
        
        try:
            # Ensure parent directory exists
            # Example: for "data/output.txt", create "data/" if needed
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file asynchronously
            # mode='w' = write mode (overwrites existing file)
            # encoding='utf-8' = handle Unicode characters properly
            async with aiofiles.open(file_path, mode='w', encoding='utf-8') as file:
                await file.write(content)
            
            # Return helpful message
            return f"Successfully wrote {len(content)} characters to {file_path}"
            
        except PermissionError:
            raise PermissionError(f"Permission denied writing to {file_path}")
        except Exception as e:
            raise Exception(f"Error writing file {file_path}: {str(e)}")


# LEARNING QUESTIONS:
# Q1: Why do we check 'content is None' instead of 'not content'?
# A1: Because empty string "" is valid content, but 'not ""' would be True
#     and reject it. We only want to reject None (missing parameter).

# Q2: What does 'parents=True, exist_ok=True' do?
# A2: parents=True creates all parent directories if they don't exist
#     exist_ok=True doesn't raise error if directory already exists
#     Similar to 'mkdir -p' in Unix

# Q3: Why use Path() from pathlib?
# A3: Path provides cross-platform file path handling (Windows vs Unix)
#     and convenient methods like .parent, .exists(), .mkdir()
