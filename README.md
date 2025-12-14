# Temporal Agent Execution with Message Buffering

This project demonstrates using Temporal workflows to execute AI agents with intelligent message buffering for group chat scenarios.

## Features

### 1. Simple Agent Execution

- Basic workflow that executes an agent with a single query
- Uses OpenAI Agents with handoff capabilities (triage → specialist)

### 2. Buffered Agent Execution

- **Smart message buffering** for group chat scenarios
- **Delay mechanism**: Waits 5 seconds after each message
- **Timer reset**: New messages reset the 5-second countdown
- **Bulk processing**: Once the timer expires, all messages are processed together
- **Signals & Queries**: Add messages via signals, check status via queries

## Architecture

```
┌─────────────────┐
│  Group Chat     │
│  Messages       │
└────────┬────────┘
         │ Signal: add_message()
         ▼
┌─────────────────────────────────┐
│  BufferedAgentExecution         │
│  Workflow                       │
│                                 │
│  • Buffer messages              │
│  • 5-second delay timer         │
│  • Reset timer on new message   │
│  • Bulk process when timer ends │
└────────┬────────────────────────┘
         │ Activity: execute_agent()
         ▼
┌─────────────────────────────────┐
│  Agent System                   │
│                                 │
│  Triage Agent ──────► Task Agent│
│  (orchestrator)     (tools)     │
│                                 │
│  Tools:                         │
│  • get_weather()                │
│  • search_database()            │
└─────────────────────────────────┘
```

## How the Buffer Works

1. **Initial Message**: Workflow starts with first message
2. **Timer Start**: Begins 5-second countdown
3. **New Message Arrives**: Timer resets to 5 seconds
4. **Repeat**: Each new message resets the timer
5. **Timer Expires**: No messages for 5 seconds → process all buffered messages
6. **Bulk Processing**: Agent receives all messages at once for context-aware response

## Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Start Temporal Server

```bash
temporal server start-dev
```

### 3. Run the Worker

In a new terminal:

```bash
uv run run_worker.py
```

## Usage

### Simple Agent Execution

```bash
uv run run_workflow.py
```

This executes a single query: "What's the weather like in San Francisco?"

### Buffered Agent Execution

```bash
uv run run_buffered_workflow.py
```

This demonstrates the buffering mechanism:

- Starts with initial weather question
- Sends 3 additional messages at 1-2 second intervals
- Each message resets the 5-second timer
- After the last message, waits 5 seconds then processes all messages together

## Workflow Components

### Workflows (`workflows.py`)

1. **AgentExecution**: Simple single-query execution
2. **BufferedAgentExecution**: Smart buffering with signals
   - Signal: `add_message(message: str)` - Add message to buffer
   - Query: `get_buffer_status()` - Check buffer state

### Activities (`activities.py`)

- **execute_agent(user_query: str)**: Executes the agent system with a query

### Agent System (`agents/main.py`)

- **Triage Agent**: Routes requests to appropriate handlers
- **Task Agent**: Has access to tools (weather, database search)

## Monitoring

View the Temporal UI at: http://localhost:8233

You can see:

- Workflow executions
- Signal events (messages being added)
- Query results (buffer status)
- Activity executions (agent processing)
- Complete event history

## Customization

### Adjust Buffer Delay

In `workflows.py`, modify:

```python
self.buffer_delay_seconds = 5  # Change to your desired seconds
```

### Add More Tools

In `agents/main.py`, add new function tools:

```python
@function_tool
def your_new_tool(param: str) -> str:
    """Your tool description"""
    return "result"

# Add to task_agent
task_agent = Agent(
    name="Task Agent",
    instructions=specialist_instructions,
    tools=[get_weather, search_database, your_new_tool]
)
```

## Use Cases

- **Group Chat Moderation**: Buffer messages, analyze sentiment in bulk
- **Customer Support**: Batch similar queries for efficient processing
- **Content Aggregation**: Collect related posts before generating summaries
- **Rate Limiting**: Control API calls by batching requests
- **Cost Optimization**: Reduce LLM API calls by processing messages together

## Benefits of Temporal

- **Durable Execution**: Workflows survive crashes and restarts
- **Built-in Retry Logic**: Automatic retries for transient failures
- **Visibility**: Complete audit trail of all events
- **Signals**: Asynchronous message passing without polling
- **Queries**: Read workflow state without affecting execution
- **Timeouts**: Built-in timeout handling at activity and workflow level
