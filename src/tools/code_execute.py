"""
CodeExecuteTool - Safely executes Python code

LEARNING POINTS:
- Uses subprocess for isolation (security!)
- Captures both stdout and stderr
- Implements timeout to prevent infinite loops
- Returns structured result with output and errors
- WARNING: Code execution is inherently dangerous - use with caution!
"""

import asyncio
import sys
from typing import Dict
from src.core.base_tool import BaseTool


class CodeExecuteTool(BaseTool):
    """
    A tool that executes Python code safely in a subprocess.
    
    SECURITY CONSIDERATIONS:
    - Runs code in a separate process (isolated from main program)
    - Has timeout to prevent infinite loops
    - Still dangerous - don't run untrusted code!
    - In production, you'd want sandboxing (Docker, etc.)
    
    Why subprocess vs exec()?
    - exec() runs in same process - can crash the agent
    - subprocess isolates execution
    - subprocess allows timeout control
    - subprocess can't access agent's memory/variables
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the code executor.
        
        Args:
            timeout: Maximum seconds to allow code to run (default 30)
        """
        self.timeout = timeout
    
    @property
    def name(self) -> str:
        return "code_execute"
    
    @property
    def description(self) -> str:
        return f"Executes Python code safely in an isolated subprocess with {self.timeout}s timeout"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute"
                }
            },
            "required": ["code"]
        }
    
    async def execute(self, params: dict) -> Dict[str, str]:
        """
        Execute Python code and return the results.
        
        Process:
        1. Validate code parameter
        2. Create subprocess with Python interpreter
        3. Pass code via stdin (safer than temp files)
        4. Wait for completion with timeout
        5. Capture stdout and stderr
        6. Return structured result
        
        Returns:
            Dict with keys:
            - success: bool (True if no errors)
            - stdout: str (printed output)
            - stderr: str (error messages)
            - exit_code: int (0 = success, non-zero = error)
        """
        code = params.get("code")
        
        if not code:
            raise ValueError("code parameter is required")
        
        try:
            # Create subprocess that runs Python
            # stdin=PIPE: we'll send code through stdin
            # stdout=PIPE: capture printed output
            # stderr=PIPE: capture errors
            # text=True: handle strings, not bytes
            process = await asyncio.create_subprocess_exec(
                sys.executable,  # Path to current Python interpreter
                "-c",            # Execute code from command line
                code,            # The code to execute
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                text=True
            )
            
            # Wait for process to complete (or timeout)
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                # Kill the process if it takes too long
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Execution timed out after {self.timeout} seconds",
                    "exit_code": -1
                }
            
            # Check if execution was successful
            success = process.returncode == 0
            
            return {
                "success": success,
                "stdout": stdout or "",  # Use empty string if None
                "stderr": stderr or "",
                "exit_code": process.returncode
            }
            
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Error executing code: {str(e)}",
                "exit_code": -1
            }


# LEARNING QUESTIONS:
# Q1: Why use subprocess instead of exec() or eval()?
# A1: exec()/eval() run in the same process and can:
#     - Access and modify agent's variables
#     - Crash the entire agent if code has errors
#     - Cannot be timed out
#     Subprocess provides isolation and control.

# Q2: What does 'sys.executable' do?
# A2: Returns the path to the Python interpreter running this code.
#     Ensures the subprocess uses the same Python version/environment.

# Q3: Why return a dict instead of just the output string?
# A3: Agents need to know:
#     - Did it succeed or fail?
#     - What was the output?
#     - Were there errors?
#     - What was the exit code?
#     Rich structured data enables better decision making.

# Q4: Is this safe for production?
# A4: NO! This is educational. Production needs:
#     - Docker containers for isolation
#     - Resource limits (CPU, memory)
#     - Restricted filesystem access
#     - Network isolation
#     - Code analysis before execution
