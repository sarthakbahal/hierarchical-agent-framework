"""
Advanced Orchestration Example - Multi-agent coordination

This example demonstrates:
1. Using the OrchestratorAgent to coordinate multiple agents
2. Complex task decomposition
3. Sequential agent execution
4. Result synthesis

This is where the hierarchical architecture shines!
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.orchestrator import OrchestratorAgent
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger("AdvancedExample")


async def example_simple_orchestration():
    """
    Example 1: Simple task orchestration
    
    Let orchestrator decide how to handle a task.
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE 1: Simple Orchestration")
    logger.info("=" * 60)
    
    # Create orchestrator
    orchestrator = OrchestratorAgent()
    
    # Give it a task that requires planning
    task = "Create a Python module for calculating statistics (mean, median, mode) with proper tests"
    
    logger.info(f"Task: {task}")
    logger.info("\nOrchestrator deciding on strategy...\n")
    
    # Let orchestrator handle it
    result = await orchestrator.execute(task)
    
    print(result)
    print("\n")
    
    # Show delegation log
    logger.info("Delegation Log:")
    for entry in orchestrator.get_delegation_log():
        logger.info(f"  - {entry['agent']}: {entry['task'][:50]}... [{'✅' if entry['success'] else '❌'}]")
    print()


async def example_complex_orchestration():
    """
    Example 2: Complex task with explicit orchestration
    
    Shows the full planning → execution workflow.
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE 2: Complex Orchestration")
    logger.info("=" * 60)
    
    orchestrator = OrchestratorAgent()
    
    # Complex task requiring multiple steps
    task = """Create a complete Python project for a URL shortener:
1. Create project structure (folders, __init__.py files)
2. Implement URL shortener class with encode/decode methods
3. Add a simple CLI interface
4. Include README with usage instructions
5. Add requirements.txt if needed"""
    
    logger.info(f"Task: {task}")
    logger.info("\nOrchestrator coordinating agents...\n")
    
    # Use explicit complex task method
    result = await orchestrator.execute_complex_task(task)
    
    print(result)
    print("\n")
    
    # Show what happened
    logger.info("What the Orchestrator did:")
    for i, entry in enumerate(orchestrator.get_delegation_log(), 1):
        agent_name = entry['agent']
        success = '✅' if entry['success'] else '❌'
        logger.info(f"{i}. Delegated to {agent_name} {success}")
        logger.info(f"   Task: {entry['task'][:80]}...")
    print()


async def example_sequential_agents():
    """
    Example 3: Sequential agent usage
    
    Shows how to use individual agents in sequence manually.
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE 3: Manual Sequential Coordination")
    logger.info("=" * 60)
    
    orchestrator = OrchestratorAgent()
    
    # Step 1: Plan
    logger.info("Step 1: Creating plan with PlannerAgent")
    plan = await orchestrator.delegate_to_planner(
        "Plan the implementation of a simple calculator app with GUI"
    )
    print("PLAN:")
    print(plan)
    print("\n")
    
    # Step 2: Execute first part of plan
    logger.info("Step 2: Implementing core logic with CoderAgent")
    code_result = await orchestrator.delegate_to_coder(
        "Based on this plan, create the calculator.py file with basic arithmetic operations",
        context={"plan": plan}
    )
    print("CODER RESULT:")
    print(code_result)
    print("\n")
    
    # Step 3: Synthesize
    logger.info("Step 3: Synthesizing final result")
    final = await orchestrator.execute(
        f"Summarize what we accomplished:\nPlan:\n{plan}\n\nImplementation:\n{code_result}"
    )
    print("FINAL SUMMARY:")
    print(final)
    print("\n")


async def example_error_handling():
    """
    Example 4: Error handling in orchestration
    
    Shows what happens when tasks fail.
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE 4: Error Handling")
    logger.info("=" * 60)
    
    orchestrator = OrchestratorAgent()
    
    try:
        # This might fail if path doesn't exist or permissions issue
        task = "Read the file '/nonexistent/path/file.txt' and summarize it"
        
        logger.info(f"Task: {task}")
        logger.info("(This should fail gracefully)\n")
        
        result = await orchestrator.execute(task)
        print(result)
        
    except Exception as e:
        logger.warning(f"Expected error occurred: {str(e)}")
        logger.info("Orchestrator handled the error appropriately")
    
    print("\n")


async def main():
    """Run all advanced examples."""
    logger.info("🚀 Starting Advanced Orchestration Examples")
    logger.info("These examples show multi-agent coordination in action\n")
    
    try:
        # Example 1: Simple orchestration
        await example_simple_orchestration()
        
        # Example 2: Complex orchestration
        await example_complex_orchestration()
        
        # Example 3: Manual sequential coordination
        await example_sequential_agents()
        
        # Example 4: Error handling
        await example_error_handling()
        
        logger.info("=" * 60)
        logger.info("✅ All advanced examples completed!")
        logger.info("=" * 60)
        
        logger.info("\nKey Takeaways:")
        logger.info("1. Orchestrator intelligently delegates to specialized agents")
        logger.info("2. Complex tasks are broken down automatically")
        logger.info("3. Agents work sequentially, building on each other's results")
        logger.info("4. Error handling prevents system crashes")
        logger.info("5. Delegation log helps debug multi-agent workflows")
        
    except Exception as e:
        logger.error(f"❌ Error in advanced examples: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())


# LEARNING POINTS:
# 1. Orchestrator is the "project manager" of the agent system
# 2. It decides which agents to use based on task analysis
# 3. Agents work sequentially (later agents use earlier results)
# 4. Delegation log tracks the orchestration flow
# 5. Error handling prevents cascade failures

# ARCHITECTURE INSIGHTS:
# - OrchestratorAgent contains PlannerAgent and CoderAgent
# - Each agent is independent but can be coordinated
# - Hierarchical: User → Orchestrator → Specialized Agents
# - Flexible: Can use agents individually or through orchestrator

# TRY THIS:
# 1. Run: python examples/advanced_orchestration.py
# 2. Watch the delegation log to see decision-making
# 3. Try your own complex tasks
# 4. Add more specialized agents (ReviewerAgent, TesterAgent, etc.)
# 5. Experiment with parallel delegation (advanced!)

# NEXT STEPS:
# - Add more specialized agents
# - Implement result caching
# - Add parallel task execution
# - Build a web interface
# - Add conversation memory across sessions
