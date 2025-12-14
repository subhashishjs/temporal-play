import asyncio
from temporalio.client import Client
from workflows import BufferedAgentExecution

async def main():
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233")
    
    # Start the workflow with an initial message
    print("Starting buffered workflow with initial message...")
    workflow_handle = await client.start_workflow(
        BufferedAgentExecution.run,
        "What's the weather like in San Francisco?",
        id="buffered-agent-workflow",
        task_queue="agent-execution"
    )
    
    print("Workflow started! Workflow ID:", workflow_handle.id)
    
    # Simulate messages arriving at different times
    print("\n--- Simulating incoming messages ---")
    
    # Send first message after 1 second
    await asyncio.sleep(1)
    print("Sending message 1...")
    await workflow_handle.signal(BufferedAgentExecution.add_message, "Also check the weather in New York")
    
    # Send second message after 2 more seconds (timer should reset)
    await asyncio.sleep(2)
    print("Sending message 2...")
    await workflow_handle.signal(BufferedAgentExecution.add_message, "And what about Los Angeles?")
    
    # Send third message after 2 more seconds (timer should reset again)
    await asyncio.sleep(2)
    print("Sending message 3...")
    await workflow_handle.signal(BufferedAgentExecution.add_message, "Finally, check Chicago weather")
    
    # Now wait without sending more messages - the 5 second timer should complete
    print("\nNo more messages being sent. Waiting for workflow to process buffer...")
    
    # Query the buffer status while waiting
    await asyncio.sleep(2)
    status = await workflow_handle.query(BufferedAgentExecution.get_buffer_status)
    print(f"\nBuffer status: {status}")
    
    # Wait for the workflow to complete
    print("\nWaiting for workflow result...")
    result = await workflow_handle.result()
    
    print("\n" + "="*60)
    print("WORKFLOW RESULT:")
    print("="*60)
    print(result)
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
