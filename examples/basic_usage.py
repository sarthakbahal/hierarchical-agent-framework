"""
Basic Usage Example - Simple agent interactions

This example demonstrates:
1. Using individual agents directly
2. Reading and writing files
3. Creating plans
4. Writing code

Start here to understand how each agent works!
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.planner import PlannerAgent
from src.agents.coder import CoderAgent
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger("BasicExample")


async def example_planner():
    """
    Example 1: Using the PlannerAgent
    
    Shows how to create execution plans for complex tasks.
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE 1: PlannerAgent")
    logger.info("=" * 60)
    
    # Create planner agent
    planner = PlannerAgent()
    
    # Give it a task to plan
    task = "Build a simple todo list web application with Python backend and HTML/CSS/JS frontend"
    
    logger.info(f"Task: {task}")
    logger.info("\nGenerating plan...\n")
    
    # Get the plan
    plan = await planner.create_plan(task)
    
    # Display the plan
    print(plan)
    print("\n")


async def example_coder():
    """
    Example 2: Using the CoderAgent
    
    Shows how to write code with the agent.
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE 2: CoderAgent")
    logger.info("=" * 60)
    
    # Create coder agent
    coder = CoderAgent()
    
    # Give it a coding task
    task = """Create a Python script called 'greet.py' that:
1. Defines a function called greet(name) that returns a greeting message
2. Includes proper docstrings
3. Has a main block that demonstrates usage
4. Follows best practices"""
    
    logger.info(f"Task: {task}")
    logger.info("\nWriting code...\n")
    
    # Execute the task
    result = await coder.write_code(task)
    
    # Display what the agent did
    print(result)
    print("\n")
    
    # Check if file was created
    if Path("greet.py").exists():
        logger.info("✅ File 'greet.py' was created successfully!")
        logger.info("Reading file contents:")
        print("\n" + "=" * 60)
        print(Path("greet.py").read_text())
        print("=" * 60 + "\n")


async def example_file_operations():
    """
    Example 3: File operations with CoderAgent
    
    Shows how agents use tools to read/write files.
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE 3: File Operations")
    logger.info("=" * 60)
    
    coder = CoderAgent()
    
    # Create a test file
    logger.info("Creating test file 'data.txt'")
    task1 = "Create a file called 'data.txt' with a list of 5 programming languages, one per line"
    result1 = await coder.execute(task1)
    print(result1)
    print()
    
    # Read the file back
    logger.info("Reading the file back")
    task2 = "Read the contents of 'data.txt' and tell me how many languages are listed"
    result2 = await coder.execute(task2)
    print(result2)
    print()
    
    # Modify the file
    logger.info("Modifying the file")
    task3 = "Add 3 more programming languages to 'data.txt'"
    result3 = await coder.execute(task3)
    print(result3)
    print("\n")


async def main():
    """Run all examples."""
    logger.info("🚀 Starting Basic Usage Examples")
    logger.info("Make sure you have set up your .env file with API keys!\n")
    
    try:
        # Example 1: Planning
        await example_planner()
        
        # Example 2: Coding
        await example_coder()
        
        # Example 3: File Operations
        await example_file_operations()
        
        logger.info("=" * 60)
        logger.info("✅ All examples completed successfully!")
        logger.info("=" * 60)
        
        logger.info("\nFiles created:")
        for file in ["greet.py", "data.txt"]:
            if Path(file).exists():
                logger.info(f"  - {file}")
        
    except Exception as e:
        logger.error(f"❌ Error running examples: {str(e)}")
        logger.error("\nMake sure:")
        logger.error("1. You created .env file (copy from .env.example)")
        logger.error("2. You added your API key")
        logger.error("3. You installed dependencies: pip install -r requirements.txt")
        raise


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())


# LEARNING POINTS:
# 1. Agents are easy to use - just create and call methods
# 2. Agents handle tool usage automatically
# 3. All agent methods are async (use await)
# 4. Agents log their actions (helps debugging)
# 5. File operations happen through agents (they decide which tools to use)

# TRY THIS:
# 1. Run this script: python examples/basic_usage.py
# 2. Examine the generated files
# 3. Modify the tasks and see what agents do differently
# 4. Add your own examples!

# NEXT STEPS:
# - See advanced_orchestration.py for multi-agent coordination
# - Try giving agents more complex tasks
# - Experiment with different prompts
# - Add new tools and see agents use them
