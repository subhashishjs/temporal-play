from datetime import timedelta
from temporalio import workflow

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