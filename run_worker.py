import asyncio
import concurrent.futures
from temporalio.client import Client
from temporalio.worker import Worker

# Braintrust logger for stimulation
import braintrust
from braintrust.wrappers.openai import BraintrustTracingProcessor

from agents import set_trace_processors

# Import the activity and workflow from our other files
from activities import execute_agent
from workflows import AgentExecution, BufferedAgentExecution


temporal_playground_logger = braintrust.init_logger(
    project="temporal-playground",
)

set_trace_processors([BraintrustTracingProcessor(logger=temporal_playground_logger)])

async def main():
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233")

    # Run the worker
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as activity_executor:
        worker = Worker(
          client,
          task_queue="agent-execution",
          workflows=[AgentExecution, BufferedAgentExecution],
          activities=[execute_agent],
          activity_executor=activity_executor,
        )
        await worker.run()

if __name__ == "__main__":
    asyncio.run(main())