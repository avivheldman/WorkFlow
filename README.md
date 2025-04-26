# Workflow Engine

A flexible and extensible workflow engine built with Python and FastAPI that allows you to define and execute tasks in sequence or parallel.

## Features

- **Task Management**: Define and execute individual tasks
- **Workflow Management**: Organize tasks into sequential or parallel execution steps
- **State Persistence**: Store workflow states in Redis or in-memory
- **REST API**: Interact with workflows via a RESTful API
- **Graceful Fallback**: Automatically falls back to in-memory storage if Redis is unavailable

## Architecture

The project follows a clean, modular architecture:

- **Core Components**: Task, Execution, Repository, and Workflow engines
- **API Layer**: FastAPI endpoints for workflow management
- **Data Models**: Pydantic models for data validation and serialization

### Data Flow

```
┌──────────┐    ┌─────────────┐    ┌───────────────┐    ┌────────────────┐
│  Client  │───▶│ FastAPI     │───▶│ WorkflowEngine │───▶│ WorkflowFactory│
│  Request │    │ Router      │    │                │    │                │
└──────────┘    └─────────────┘    └───────┬───────┘    └────────────────┘
                                           │
                                           ▼
┌──────────┐    ┌─────────────┐    ┌───────────────┐
│ Redis/   │◀───│ Repository  │◀───│ Task Execution │
│ Memory   │    │             │    │                │
└──────────┘    └─────────────┘    └───────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- Redis (optional, for persistent storage)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/workflow-engine.git
   cd workflow-engine
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start Redis (optional):
   ```bash
   # On Linux/Mac
   redis-server

   # On Windows, start the Redis server executable
   # Or use Docker:
   docker run -p 6379:6379 redis
   ```

## Usage

### Starting the API Server

```bash
uvicorn app.main:app --reload
```

The API will be accessible at http://localhost:8000. API documentation is available at http://localhost:8000/docs.

### Creating a Workflow

Send a POST request to `/api/workflow`:

```bash
curl -X POST "http://localhost:8000/api/workflow" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "sample_workflow",
       "steps": [
         {
           "execution_type": "sequential",
           "tasks": [
             {
               "name": "task_a",
               "params": { "timeout": 30 }
             },
             {
               "name": "task_b",
               "params": { "retry_count": 3 }
             }
           ]
         },
         {
           "execution_type": "parallel",
           "tasks": [
             {
               "name": "task_c",
               "params": { "priority": "high" }
             }
           ]
         }
       ]
     }'
```

### Getting Workflow Status

```bash
# Get specific workflow by ID
curl -X GET "http://localhost:8000/api/workflow/YOUR_WORKFLOW_ID"

# Get all workflows
curl -X GET "http://localhost:8000/api/workflows"
```

## Adding Custom Tasks

1. Create your task class in `app/core/tasks.py`:

```python
class MyCustomTask(Task):
    def __init__(self):
        super().__init__("my_custom_task")

    async def execute(self) -> bool:
        try:
            self.set_status(TaskStatus.RUNNING)
            logger.info("Running my custom task")
            # Task implementation here
            self.set_status(TaskStatus.SUCCEEDED)
            return True
        except Exception as e:
            logger.error(f"Error in my custom task: {e}")
            self.set_status(TaskStatus.FAILED)
            return False
```

2. Register your task in `app/core/task_factory.py`:

```python
@staticmethod
def create_task(task_name: str) -> Task:
    tasks = {
        "task_a": TaskA(),
        "task_b": TaskB(),
        "task_c": TaskC(),
        "my_custom_task": MyCustomTask(),  # Add your task here
    }
    # ...
```

## Project Structure

```
app/
├── core/
│   ├── execution.py     # Execution strategies
│   ├── repository.py    # State repositories
│   ├── repository_factory.py # Repository management
│   ├── task_factory.py  # Task creation
│   ├── tasks.py         # Task definitions
│   └── workflow.py      # Workflow engine
├── routers/
│   └── workflow.py      # API endpoints
├── schemas/
│   └── workflow.py      # Data models
├── config.py            # Configuration
└── main.py              # FastAPI application
```

## Configuration

Configuration settings are in `app/config.py`. You can override these using environment variables:

```bash
# Redis configuration
export REDIS_HOST=redis.example.com
export REDIS_PORT=6379
export REDIS_PASSWORD=your_password

# Application settings
export DEBUG=True
export MAX_CONCURRENT_WORKFLOWS=20
```