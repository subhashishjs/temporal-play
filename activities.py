from temporalio import activity


@activity.defn
def execute_agent(user_query: str) -> str:
    """Execute the agent system with a user request.
    
    Args:
        user_query: The user's query/request to process
        
    Returns:
        The agent's response as a string
    """
    import sys
    from pathlib import Path
    import importlib.util
    
    # Load agents.main module directly to avoid import conflicts
    agents_main_path = Path(__file__).parent / "agents" / "main.py"
    spec = importlib.util.spec_from_file_location("agents_main", agents_main_path)
    agents_main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agents_main)
    
    # Get the triage_agent from the loaded module
    triage_agent = agents_main.triage_agent
    
    # Import Runner from the external agents library
    from agents import Runner
    
    # Use run_sync for synchronous execution
    result = Runner.run_sync(triage_agent, user_query)
    
    # Extract the final message from the result
    if hasattr(result, 'final_message') and result.final_message:
        return str(result.final_message)
    
    return str(result)