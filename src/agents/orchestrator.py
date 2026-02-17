"""
OrchestratorAgent - Coordinates multiple specialized agents

LEARNING POINTS:
- Hierarchical agent coordination
- Task decomposition and delegation
- Agent selection strategy
- Result synthesis
- Error recovery

Role:
- Analyzes complex tasks
- Decides which agents to use
- Delegates subtasks
- Synthesizes results
- Handles failures gracefully

This is the "brain" of the multi-agent system!
"""

from src.core.base_agent import BaseAgent
from src.core.llm_client import LLMClient
from src.agents.planner import PlannerAgent
from src.agents.coder import CoderAgent
from typing import Optional, List, Dict, Any
from src.core.base_tool import BaseTool


class OrchestratorAgent(BaseAgent):
    """
    Meta-agent that coordinates other specialized agents.
    
    Think of this as a Project Manager or Tech Lead:
    - Understands the big picture
    - Knows each agent's capabilities
    - Delegates work appropriately
    - Synthesizes results
    - Handles coordination and communication
    
    Architecture:
    - User gives task to Orchestrator
    - Orchestrator analyzes and creates strategy
    - Orchestrator calls specialized agents (Planner, Coder, etc.)
    - Orchestrator combines results
    - Orchestrator returns final result to user
    
    When to use:
    - Complex tasks requiring multiple skills
    - Tasks that benefit from planning
    - Tasks requiring coordination of multiple steps
    """
    
    def __init__(
        self,
        tools: Optional[List[BaseTool]] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize the Orchestrator Agent.
        
        Creates instances of specialized agents to delegate to.
        Can optionally have its own tools too.
        """
        super().__init__(
            name="OrchestratorAgent",
            tools=tools or [],
            llm_client=llm_client
        )
        
        # Create specialized agents
        # They share the same LLM client for efficiency
        self.planner = PlannerAgent(llm_client=self.llm_client)
        self.coder = CoderAgent(llm_client=self.llm_client)
        
        # Keep track of delegated tasks for logging/debugging
        self.delegation_log: List[Dict[str, Any]] = []
    
    @property
    def system_prompt(self) -> str:
        """
        Define the Orchestrator's role and capabilities.
        
        Key aspects:
        - Understands when to delegate
        - Knows each agent's strengths
        - Coordinates workflow
        - Synthesizes results
        """
        return """You are an expert Project Manager and Technical Orchestrator.

Your role is to coordinate specialized AI agents to accomplish complex tasks.

You have access to these specialized agents:
1. **PlannerAgent**: Creates detailed execution plans for complex tasks
   - Use for: Breaking down complex problems, designing architecture
   - Strength: Strategic thinking, identifying dependencies

2. **CoderAgent**: Writes and modifies code
   - Use for: Implementing features, writing code, modifying files
   - Strength: Clean code, best practices, file manipulation
   - Tools: file_read, file_write, list_directory

When given a task, you should:
1. **Analyze**: Understand what needs to be done
2. **Strategize**: Decide which agents to use and in what order
3. **Delegate**: Call appropriate agents with clear subtasks
4. **Synthesize**: Combine results into coherent final output
5. **Validate**: Ensure task was completed successfully

Your decision making:
- **Simple tasks**: Handle directly without delegation
- **Planning needed**: Use PlannerAgent first, then execute plan
- **Code required**: Use CoderAgent with specific instructions
- **Complex tasks**: Use multiple agents in sequence

Communication with agents:
- Give clear, specific instructions
- Provide necessary context
- One agent at a time (sequential, not parallel)
- Use agent results to inform next steps

Output format:
When delegating, format your thoughts as:
```
ANALYSIS: [Brief analysis of the task]
STRATEGY: [Which agents to use and why]
DELEGATION TO [Agent Name]: [Specific subtask]
```

After receiving results, synthesize into a clear final response for the user."""
    
    async def delegate_to_planner(self, task: str) -> str:
        """
        Delegate a planning task to the PlannerAgent.
        
        Args:
            task: Planning task description
            
        Returns:
            Plan created by PlannerAgent
        """
        self.logger.info(f"Delegating to PlannerAgent: {task[:100]}...")
        
        try:
            result = await self.planner.create_plan(task)
            
            # Log delegation for tracking
            self.delegation_log.append({
                "agent": "PlannerAgent",
                "task": task,
                "success": True
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"PlannerAgent failed: {str(e)}")
            self.delegation_log.append({
                "agent": "PlannerAgent",
                "task": task,
                "success": False,
                "error": str(e)
            })
            raise
    
    async def delegate_to_coder(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Delegate a coding task to the CoderAgent.
        
        Args:
            task: Coding task description
            context: Optional context (file paths, existing code, etc.)
            
        Returns:
            Result from CoderAgent
        """
        self.logger.info(f"Delegating to CoderAgent: {task[:100]}...")
        
        try:
            result = await self.coder.execute(task, context)
            
            self.delegation_log.append({
                "agent": "CoderAgent",
                "task": task,
                "success": True
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"CoderAgent failed: {str(e)}")
            self.delegation_log.append({
                "agent": "CoderAgent",
                "task": task,
                "success": False,
                "error": str(e)
            })
            raise
    
    async def execute_complex_task(self, task: str) -> str:
        """
        Execute a complex task using multiple agents.
        
        Workflow:
        1. Analyze task (using LLM)
        2. Create plan (using PlannerAgent)
        3. Execute plan (using CoderAgent or other agents)
        4. Synthesize results
        
        Args:
            task: Complex task description
            
        Returns:
            Final result after orchestration
        """
        self.logger.info(f"Orchestrating complex task: {task[:100]}...")
        
        # Step 1: Analyze and strategize
        analysis = await self.execute(
            f"Analyze this task and decide on execution strategy: {task}"
        )
        
        self.logger.debug(f"Analysis result: {analysis[:200]}...")
        
        # Step 2: Create plan
        if "plan" in analysis.lower() or "complex" in analysis.lower():
            self.logger.info("Task requires planning, delegating to PlannerAgent")
            plan = await self.delegate_to_planner(task)
            
            # Step 3: Execute plan with appropriate agents
            # For now, we'll delegate to CoderAgent if it involves code
            if any(keyword in task.lower() for keyword in ["code", "implement", "write", "create file"]):
                self.logger.info("Executing plan with CoderAgent")
                result = await self.delegate_to_coder(
                    f"Execute this plan:\n\n{plan}",
                    context={"plan": plan}
                )
            else:
                result = plan  # Plan is the result for non-code tasks
        else:
            # Simple task, handle directly
            result = analysis
        
        # Step 4: Synthesize final result
        final_result = await self.execute(
            f"Synthesize these results into a final response:\n\nTask: {task}\n\nResults:\n{result}"
        )
        
        self.logger.info("Complex task orchestration completed")
        return final_result
    
    def get_delegation_log(self) -> List[Dict[str, Any]]:
        """
        Get log of all delegations made by this orchestrator.
        
        Useful for:
        - Debugging
        - Performance analysis
        - Understanding orchestration decisions
        
        Returns:
            List of delegation records
        """
        return self.delegation_log
    
    def clear_delegation_log(self):
        """Clear the delegation log."""
        self.delegation_log = []


# LEARNING QUESTIONS:
# Q1: Why does Orchestrator create agent instances instead of receiving them?
# A1: Simplifies usage - one object to create
#     Ensures agents share same LLM client (efficiency)
#     Could be made configurable via dependency injection

# Q2: Why delegate sequentially instead of in parallel?
# A2: Later agents may need results from earlier agents (dependencies)
#     Easier to debug and understand flow
#     More predictable behavior
#     Could add parallel delegation for independent tasks

# Q3: How does Orchestrator decide which agent to use?
# A3: Uses LLM to analyze task (in execute())
#     System prompt guides decision making
#     Could use explicit rules or classifiers too
#     LLM is flexible but less predictable

# Q4: Why keep delegation_log?
# A4: Debugging - see what decisions were made
#     Performance analysis - identify bottlenecks
#     Error recovery - know what succeeded/failed
#     User feedback - show what happened

# Q5: How would you prevent infinite delegation loops?
# A5: Add max_depth parameter (limit recursion)
#     Track call stack
#     Set timeout for entire orchestration
#     Agents shouldn't delegate back to orchestrator
