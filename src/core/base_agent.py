"""
BaseAgent - Abstract base class for all agents

LEARNING POINTS:
- Template Method Pattern: Define workflow, subclasses fill in details
- Async workflow execution
- Message history management
- Tool integration
- Error handling and retries
- Agent state management

Why abstract?
- Common agent behavior in one place
- Consistent interface across all agents
- Easy to add new agent types
- Enforces required methods (system_prompt, process_response)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.core.llm_client import LLMClient
from src.core.base_tool import BaseTool
from src.utils.logger import setup_logger
from src.utils.config import settings
import json


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    What's an agent?
    - Autonomous entity that uses LLM to reason and act
    - Has specific role/expertise (planner, coder, etc.)
    - Can use tools to interact with environment
    - Maintains conversation history
    - Makes decisions and takes actions
    
    Template Method Pattern:
    - execute() method defines the workflow (template)
    - Subclasses implement specific steps (system_prompt, process_response)
    - This ensures all agents follow the same workflow
    
    Workflow:
    1. Receive task
    2. Build messages with system prompt and task
    3. Call LLM
    4. Process response (may call tools)
    5. Return result
    """
    
    def __init__(
        self,
        name: str,
        tools: Optional[List[BaseTool]] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize the agent.
        
        Args:
            name: Agent's name (for logging and identification)
            tools: List of tools this agent can use
            llm_client: LLM client (creates one if not provided)
        """
        self.name = name
        self.tools = tools or []
        self.llm_client = llm_client or LLMClient()
        self.logger = setup_logger(f"Agent.{name}")
        
        # Message history for this agent
        # Maintains context across multiple interactions
        self.message_history: List[Dict[str, str]] = []
        
        # Tool lookup dictionary for fast access
        # {tool_name: tool_instance}
        self.tool_map = {tool.name: tool for tool in self.tools}
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """
        Define the agent's role, personality, and capabilities.
        
        This is THE MOST IMPORTANT part of an agent!
        The system prompt defines:
        - Who the agent is
        - What it's good at
        - How it should behave
        - What tools it has
        - How to format responses
        
        Example:
            "You are an expert Python developer. You write clean,
            efficient code following best practices. You have access
            to file tools to read and write code."
        """
        pass
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute a task.
        
        This is the main method that external code calls.
        It implements the Template Method pattern.
        
        Workflow:
        1. Log task start
        2. Add task to message history
        3. Generate LLM response
        4. Process response (handle tool calls if any)
        5. Log completion
        6. Return result
        
        Args:
            task: Description of what to do
            context: Optional additional context (files, data, etc.)
            
        Returns:
            str: The result of executing the task
        """
        self.logger.info(f"Executing task: {task[:100]}...")
        
        try:
            # Build message for LLM
            user_message = self._build_user_message(task, context)
            self.message_history.append({"role": "user", "content": user_message})
            
            # Get tools in LLM-friendly format if agent has tools
            tool_definitions = self._get_tool_definitions() if self.tools else None
            
            # Call LLM
            response = await self.llm_client.generate(
                messages=self.message_history,
                system_prompt=self.system_prompt,
                tools=tool_definitions
            )
            
            # Process response (may involve tool calls)
            result = await self._process_response(response)
            
            # Add result to history
            self.message_history.append({"role": "assistant", "content": result})
            
            self.logger.info(f"Task completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing task: {str(e)}")
            raise
    
    def _build_user_message(self, task: str, context: Optional[Dict[str, Any]]) -> str:
        """
        Build the user message with task and context.
        
        Why separate method?
        - Can be overridden by subclasses for custom formatting
        - Keeps execute() method clean
        - Easier to test
        
        Args:
            task: The task description
            context: Optional additional context
            
        Returns:
            Formatted message string
        """
        message = f"Task: {task}"
        
        if context:
            message += "\n\nContext:\n"
            for key, value in context.items():
                message += f"- {key}: {value}\n"
        
        return message
    
    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Convert tools to LLM-friendly format (OpenAI function calling format).
        
        Transforms our BaseTool instances into JSON schema that LLMs understand.
        
        Format:
        {
            "type": "function",
            "function": {
                "name": "tool_name",
                "description": "what it does",
                "parameters": {...}  # JSON schema
            }
        }
        
        Returns:
            List of tool definitions in OpenAI format
        """
        definitions = []
        
        for tool in self.tools:
            definitions.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        
        return definitions
    
    async def _process_response(self, response: Dict[str, Any]) -> str:
        """
        Process LLM response, handling tool calls if present.
        
        Flow:
        1. Check if LLM wants to call tools
        2. If yes, execute tools and get results
        3. Send results back to LLM
        4. Get final response
        5. If no tool calls, return content directly
        
        This method handles the ReAct pattern (Reasoning + Acting):
        - LLM reasons about what tools to use
        - We execute the tools (acting)
        - LLM reasons about the results
        - Repeat until task is done
        
        Args:
            response: Response dict from LLM
            
        Returns:
            Final text response
        """
        # Check for tool calls
        tool_calls = response.get("tool_calls", [])
        
        if not tool_calls:
            # No tools needed, return content directly
            return response.get("content", "")
        
        # Execute tool calls
        self.logger.info(f"Processing {len(tool_calls)} tool calls")
        
        tool_results = []
        for tool_call in tool_calls:
            result = await self._execute_tool_call(tool_call)
            tool_results.append(result)
        
        # Add tool results to message history
        # Format depends on provider (this is OpenAI format)
        self.message_history.append({
            "role": "assistant",
            "content": response.get("content") or "",
            "tool_calls": tool_calls
        })
        
        for result in tool_results:
            self.message_history.append({
                "role": "tool",
                "tool_call_id": result["tool_call_id"],
                "content": result["content"]
            })
        
        # Get final response from LLM with tool results
        final_response = await self.llm_client.generate(
            messages=self.message_history,
            system_prompt=self.system_prompt,
            tools=self._get_tool_definitions()
        )
        
        return final_response.get("content", "")
    
    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single tool call.
        
        Args:
            tool_call: Tool call dict from LLM
            
        Returns:
            Dict with tool_call_id and result content
        """
        # Extract tool info from call
        tool_name = tool_call["function"]["name"]
        tool_args = json.loads(tool_call["function"]["arguments"])
        tool_call_id = tool_call["id"]
        
        self.logger.debug(f"Executing tool: {tool_name} with args: {tool_args}")
        
        # Get tool instance
        tool = self.tool_map.get(tool_name)
        
        if not tool:
            error_msg = f"Tool not found: {tool_name}"
            self.logger.error(error_msg)
            return {
                "tool_call_id": tool_call_id,
                "content": error_msg
            }
        
        # Execute tool
        try:
            result = await tool.execute(tool_args)
            
            # Convert result to string if needed
            if not isinstance(result, str):
                result = json.dumps(result)
            
            self.logger.debug(f"Tool {tool_name} returned: {result[:100]}...")
            
            return {
                "tool_call_id": tool_call_id,
                "content": result
            }
            
        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "tool_call_id": tool_call_id,
                "content": error_msg
            }
    
    def reset_history(self):
        """
        Clear message history.
        
        Useful when:
        - Starting a new task
        - Context is getting too long
        - Want to save tokens
        """
        self.message_history = []
        self.logger.debug("Message history reset")


# LEARNING QUESTIONS:
# Q1: Why use Template Method pattern instead of having execute() abstract?
# A1: All agents follow the same workflow (get task → call LLM → process response)
#     Only specific parts vary (system prompt, response processing)
#     Template Method avoids code duplication across agents

# Q2: Why store message_history in the agent?
# A2: LLMs are stateless - they don't remember previous messages
#     We maintain history to provide context for multi-turn conversations
#     History allows agent to reference earlier information

# Q3: Why separate _execute_tool_call from _process_response?
# A3: Single Responsibility Principle - each method does one thing
#     Easier to test, debug, and understand
#     Could override tool execution in subclasses if needed

# Q4: Why is system_prompt a property and not __init__ parameter?
# A4: Forces subclasses to define it (part of the contract)
#     Each agent type has a different prompt
#     Makes it explicit what the agent's role is
