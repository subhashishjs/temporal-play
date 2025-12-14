from agents import Agent, Runner, function_tool


@function_tool
def get_weather(location: str) -> str:
    """Get the current weather for a location.
    
    Args:
        location: The city or location to get weather for
        
    Returns:
        A string describing the weather
    """
    # Dummy implementation
    return f"The weather in {location} is sunny and 72°F"

@function_tool
def search_database(query: str) -> str:
    """Search the database for information.
    
    Args:
        query: The search query
        
    Returns:
        Search results as a string
    """
    # Dummy implementation
    return f"Found 3 results for '{query}': Result 1, Result 2, Result 3"


# Load prompts
with open("agents/prompts/triage.txt", "r") as f:
    triage_instructions = f.read()

with open("agents/prompts/specialist.txt", "r") as f:
    specialist_instructions = f.read()


# Specialist agent with tools
task_agent = Agent(
    name="Task Agent",
    instructions=specialist_instructions,
    tools=[get_weather, search_database]
)

# Triage agent that can hand off to specialist
triage_agent = Agent(
    name="Triage Agent",
    instructions=triage_instructions,
    handoffs=[task_agent]
)


# Run the agent system
if __name__ == "__main__":
    # Start with triage agent
    runner = Runner(agent=triage_agent)
    
    # Example: Run with a user query
    result = runner.run("What's the weather like in San Francisco?")
    print(result)