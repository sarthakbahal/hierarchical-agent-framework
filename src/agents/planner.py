"""
PlannerAgent - Creates execution plans for complex tasks

LEARNING POINTS:
- Specialized agent with specific role
- Minimal tool usage (planning is mostly reasoning)
- Structured output format
- Breaks down complex tasks into steps

Role:
- Analyzes tasks
- Identifies requirements
- Creates step-by-step plans
- Considers dependencies and order
"""

from src.core.base_agent import BaseAgent
from typing import Optional, List
from src.core.base_tool import BaseTool
from src.core.llm_client import LLMClient


class PlannerAgent(BaseAgent):
    """
    Agent that creates detailed execution plans for tasks.
    
    Think of this as a System Architect or Project Manager:
    - Understands requirements
    - Breaks down complex problems
    - Identifies dependencies
    - Creates actionable plans
    
    When to use:
    - Complex multi-step tasks
    - Need clear execution strategy
    - Before implementing solutions
    - Coordinating multiple components
    """
    
    def __init__(
        self,
        tools: Optional[List[BaseTool]] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize the Planner Agent.
        
        Planners typically need minimal tools (mostly reasoning).
        Can optionally give file reading tools to analyze existing code.
        """
        super().__init__(
            name="PlannerAgent",
            tools=tools or [],
            llm_client=llm_client
        )
    
    @property
    def system_prompt(self) -> str:
        """
        Define the Planner's role and behavior.
        
        Key aspects:
        - Expert in system design
        - Creates detailed, actionable plans
        - Considers dependencies
        - Structured output format
        """
        return """You are an expert System Architect and Planner.

Your role is to analyze tasks and create detailed, actionable execution plans.

When given a task, you should:
1. Analyze the requirements and constraints
2. Break down the task into clear, sequential steps
3. Identify dependencies between steps
4. Consider potential challenges and solutions
5. Provide a structured plan that can be executed by other agents

Your plan should include:
- **Goal**: Clear statement of what needs to be achieved
- **Steps**: Numbered list of actions in order
- **Dependencies**: What each step requires
- **Considerations**: Potential issues or important notes

Format your response as:
```
PLAN FOR: [task description]

GOAL:
[Clear goal statement]

STEPS:
1. [First step with details]
2. [Second step with details]
...

DEPENDENCIES:
- Step X requires: [dependencies]
- Step Y requires: [dependencies]

CONSIDERATIONS:
- [Important note 1]
- [Important note 2]
```

Be thorough but concise. Focus on actionable steps."""
    
    async def create_plan(self, task: str) -> str:
        """
        Create an execution plan for a task.
        
        This is a convenience method with a clearer name.
        Just calls execute() internally.
        
        Args:
            task: Description of what needs to be planned
            
        Returns:
            Detailed execution plan as formatted text
        """
        return await self.execute(task)


# LEARNING QUESTIONS:
# Q1: Why does PlannerAgent not need many tools?
# A1: Planning is mostly reasoning and analysis
#     The planner thinks about what to do, not how to do it
#     Execution agents (like Coder) need tools to act

# Q2: Why include the format in the system prompt?
# A2: LLMs are better at following examples than descriptions
#     Structured format makes plans easier to parse
#     Consistency across multiple planning requests

# Q3: Why create create_plan() when execute() exists?
# A3: More intuitive API - planner.create_plan(task) is clearer
#     execute() is the internal method, create_plan() is the public interface
#     Could have different planning modes (quick_plan, detailed_plan, etc.)

# Q4: How could you make plans machine-readable?
# A4: Ask LLM to output JSON format:
#     {"goal": "...", "steps": [{...}], "dependencies": {...}}
#     Could use Pydantic to validate the structure
#     Easier for Orchestrator to parse and execute
