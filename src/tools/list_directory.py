"""
ListDirectoryTool - Lists contents of a directory

LEARNING POINTS:
- Uses asyncio.to_thread() to make blocking operations async
- Returns structured data (list of dicts) instead of just strings
- Distinguishes between files and directories
- Handles both relative and absolute paths
"""

import asyncio
from pathlib import Path
from typing import List, Dict
from src.core.base_tool import BaseTool


class ListDirectoryTool(BaseTool):
    """
    A tool that lists the contents of a directory.
    
    Returns detailed information about each item:
    - name: The file/directory name
    - type: "file" or "directory"
    - path: Full path to the item
    """
    
    @property
    def name(self) -> str:
        return "list_directory"
    
    @property
    def description(self) -> str:
        return "Lists all files and subdirectories in a given directory with their types"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "The path to the directory to list"
                }
            },
            "required": ["directory_path"]
        }
    
    async def execute(self, params: dict) -> List[Dict[str, str]]:
        """
        List directory contents asynchronously.
        
        Why async here?
        - Path.iterdir() is a blocking I/O operation
        - We use asyncio.to_thread() to run it in a thread pool
        - This keeps the event loop responsive
        
        Returns:
            List of dicts, each containing:
            - name: Item name
            - type: "file" or "directory"  
            - path: Full path to item
        """
        directory_path = params.get("directory_path")
        
        if not directory_path:
            raise ValueError("directory_path parameter is required")
        
        # Convert to Path object for easier manipulation
        path = Path(directory_path)
        
        # Check if directory exists
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        try:
            # Run the blocking operation in a thread pool
            # This prevents blocking the async event loop
            items = await asyncio.to_thread(self._list_items, path)
            return items
            
        except PermissionError:
            raise PermissionError(f"Permission denied accessing {directory_path}")
        except Exception as e:
            raise Exception(f"Error listing directory {directory_path}: {str(e)}")
    
    def _list_items(self, path: Path) -> List[Dict[str, str]]:
        """
        Helper method to list directory items.
        
        Why a separate method?
        - Separates the blocking I/O logic
        - Easier to test
        - Cleaner code organization
        
        This is a synchronous method called from async context via to_thread().
        """
        items = []
        
        # Iterate through all items in the directory
        for item in path.iterdir():
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "path": str(item.absolute())  # Full path
            })
        
        # Sort for consistent ordering (directories first, then alphabetically)
        items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
        
        return items


# LEARNING QUESTIONS:
# Q1: Why use asyncio.to_thread() instead of just calling _list_items()?
# A1: Path.iterdir() is blocking - it stops the event loop while reading disk.
#     to_thread() runs it in a thread pool, keeping the event loop free
#     for other async operations.

# Q2: Why return List[Dict] instead of just List[str] of names?
# A2: Rich data is more useful to agents. They can see which items are
#     directories (to explore further) vs files (to read/write).
#     More information = better agent decisions.

# Q3: Why sort the results?
# A3: Consistent ordering makes output predictable and easier to test.
#     Directories first helps agents navigate folder structures.
