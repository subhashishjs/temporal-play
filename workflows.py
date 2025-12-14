from datetime import timedelta
from temporalio import workflow
from typing import List
import asyncio

# Import our activity, passing it through the sandbox
with workflow.unsafe.imports_passed_through():
    from activities import execute_agent

@workflow.defn
class AgentExecution:
    @workflow.run
    async def run(self, user_query: str) -> str:
        return await workflow.execute_activity(
            execute_agent, user_query, schedule_to_close_timeout=timedelta(minutes=2)
        )


@workflow.defn
class BufferedAgentExecution:
    """
    A workflow that buffers incoming messages and processes them in bulk.
    When a message arrives, it waits for 5 seconds. If another message arrives
    during this wait, the timer resets. Once 5 seconds pass without new messages,
    all buffered messages are processed together.
    """
    
    def __init__(self) -> None:
        self.message_buffer: List[str] = []
        self.new_message_received = False
        self.processing_complete = False
        self.buffer_delay_seconds = 5
    
    @workflow.signal
    def add_message(self, message: str) -> None:
        """Signal to add a new message to the buffer"""
        workflow.logger.info(f"Received message: {message}")
        self.message_buffer.append(message)
        self.new_message_received = True
    
    @workflow.query
    def get_buffer_status(self) -> dict:
        """Query to check the current buffer status"""
        return {
            "buffered_messages": len(self.message_buffer),
            "messages": self.message_buffer,
            "processing_complete": self.processing_complete
        }
    
    @workflow.run
    async def run(self, initial_message: str) -> str:
        """
        Main workflow execution. Starts with an initial message and waits for more.
        """
        # Add the initial message
        self.message_buffer.append(initial_message)
        workflow.logger.info(f"Workflow started with initial message: {initial_message}")
        
        # Wait for messages with buffer delay mechanism
        while True:
            self.new_message_received = False
            
            workflow.logger.info(
                f"Waiting {self.buffer_delay_seconds} seconds for more messages... "
                f"(Current buffer size: {len(self.message_buffer)})"
            )
            
            # Wait for either:
            # 1. A new message to arrive (resets timer)
            # 2. The delay timeout (processes buffer)
            try:
                await workflow.wait_condition(
                    lambda: self.new_message_received,
                    timeout=timedelta(seconds=self.buffer_delay_seconds)
                )
                # If we get here, a new message arrived - loop continues (timer resets)
                workflow.logger.info("New message received, resetting timer...")
            except asyncio.TimeoutError:
                # Timeout reached - no new messages, time to process
                workflow.logger.info(
                    f"No new messages for {self.buffer_delay_seconds} seconds. "
                    f"Processing {len(self.message_buffer)} messages..."
                )
                break
        
        # Combine all buffered messages
        combined_messages = "\n".join([
            f"Message {i+1}: {msg}" 
            for i, msg in enumerate(self.message_buffer)
        ])
        
        bulk_query = f"Process these {len(self.message_buffer)} messages:\n\n{combined_messages}"
        
        workflow.logger.info(f"Executing agent with bulk query")
        
        # Execute the agent activity with all buffered messages
        result = await workflow.execute_activity(
            execute_agent, 
            bulk_query,
            schedule_to_close_timeout=timedelta(minutes=2)
        )
        
        self.processing_complete = True
        workflow.logger.info("Processing complete!")
        
        return result