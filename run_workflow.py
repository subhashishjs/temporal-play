import asyncio
from temporalio.client import Client

# Import the workflow from the previous code
from workflows import AgentExecution

async def main():
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233")
    
    # Execute a workflow
    result = await client.execute_workflow(AgentExecution.run, "What's the weather like in San Francisco?", id="agent-execution-workflow", task_queue="agent-execution")

    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())