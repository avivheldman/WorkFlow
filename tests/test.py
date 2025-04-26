import asyncio
import logging
import uuid
from datetime import datetime

from app.core.repository import InMemoryStateRepository
from app.core.tasks import TaskA, TaskB, TaskC
from app.core.execution import ParallelExecution, SequentialExecution
from app.core.workflow import WorkflowEngine
from app.schemas.workflow import (
    WorkflowDefinition, StepDefinition, TaskDefinition,
    ExecutionType, WorkflowState, TaskStatus, WorkflowStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


async def test_sequential_execution():
    print("\n----- Testing Sequential Execution -----")
    tasks = [TaskA(), TaskB(), TaskC()]
    print(f"Created tasks: {[task.name for task in tasks]}")
    strategy = SequentialExecution()
    print("Executing tasks sequentially...")
    results = await strategy.execute(tasks)

    print("Execution results:")
    for task_name, success in results.items():
        print(f"  {task_name}: {'Success' if success else 'Failed'}")

    return results


async def test_parallel_execution():
    print("\n----- Testing Parallel Execution -----")
    tasks = [TaskA(), TaskB(), TaskC()]
    print(f"Created tasks: {[task.name for task in tasks]}")
    strategy = ParallelExecution()
    print("Executing tasks in parallel...")
    results = await strategy.execute(tasks)
    print("Execution results:")
    for task_name, success in results.items():
        print(f"  {task_name}: {'Success' if success else 'Failed'}")

    return results


async def test_repository():
    print("\n----- Testing State Repository -----")

    memory_repo = InMemoryStateRepository()

    # Create a valid test state that matches the WorkflowState structure
    test_state = {
        "id": str(uuid.uuid4()),
        "name": "test-workflow-name",  # Required field that was missing
        "status": WorkflowStatus.RUNNING,
        "steps": {},  # Empty steps dictionary
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    await memory_repo.save_workflow_state("test-workflow", test_state)
    retrieved_state = await memory_repo.get_workflow_state("test-workflow")

    print(f"Original state ID: {test_state['id']}")
    print(f"Retrieved state ID: {retrieved_state['id']}")

    # Test get all states
    all_states = await memory_repo.get_all_workflow_states()
    print(f"All states count: {len(all_states)}")

    # Clear the repository to avoid affecting other tests
    memory_repo._states.clear()


async def test_workflow_engine():
    print("\n----- Testing Workflow Engine -----")
    repo = InMemoryStateRepository()
    engine = WorkflowEngine(repo)
    workflow_def = WorkflowDefinition(
        name="test_workflow",
        steps=[
            StepDefinition(
                execution_type=ExecutionType.SEQUENTIAL,
                tasks=[
                    TaskDefinition(name="task_a"),
                    TaskDefinition(name="task_b")
                ]
            ),
            StepDefinition(
                execution_type=ExecutionType.PARALLEL,
                tasks=[
                    TaskDefinition(name="task_c")
                ]
            )
        ]
    )
    print("Creating workflow...")
    workflow = await engine.create_workflow(workflow_def)
    print(f"Created workflow: {workflow.id} ({workflow.name})")
    print("Executing workflow...")
    result = await engine.execute_workflow(workflow.id)
    print(f"Workflow execution complete. Status: {result.status}")

    # Verify steps were executed
    for step_idx, step in result.steps.items():
        print(f"Step {step_idx} ({step.execution_type}): {step.status}")
        for task_name, task in step.tasks.items():
            print(f"  Task {task_name}: {task.status}")

    # Get workflow by ID
    retrieved = await engine.get_workflow_state(workflow.id)
    print(f"Retrieved workflow status: {retrieved.status}")

    # Get all workflows
    all_workflows = await engine.get_all_workflows()
    print(f"Found {len(all_workflows)} workflows")

    # Clean up repository after the test
    repo._states.clear()

    return result


async def test_workflow_execution_strategies():
    print("\n----- Testing Different Execution Strategies -----")

    # Create repository
    repo = InMemoryStateRepository()

    # Create workflow engine
    engine = WorkflowEngine(repo)

    # Test sequential only workflow
    seq_workflow = WorkflowDefinition(
        name="sequential_workflow",
        steps=[
            StepDefinition(
                execution_type=ExecutionType.SEQUENTIAL,
                tasks=[
                    TaskDefinition(name="task_a"),
                    TaskDefinition(name="task_b"),
                    TaskDefinition(name="task_c")
                ]
            )
        ]
    )

    # Create and execute sequential workflow
    print("Testing sequential-only workflow...")
    workflow1 = await engine.create_workflow(seq_workflow)
    result1 = await engine.execute_workflow(workflow1.id)
    print(f"Sequential workflow status: {result1.status}")

    # Test parallel only workflow
    par_workflow = WorkflowDefinition(
        name="parallel_workflow",
        steps=[
            StepDefinition(
                execution_type=ExecutionType.PARALLEL,
                tasks=[
                    TaskDefinition(name="task_a"),
                    TaskDefinition(name="task_b"),
                    TaskDefinition(name="task_c")
                ]
            )
        ]
    )

    # Create and execute parallel workflow
    print("Testing parallel-only workflow...")
    workflow2 = await engine.create_workflow(par_workflow)
    result2 = await engine.execute_workflow(workflow2.id)
    print(f"Parallel workflow status: {result2.status}")

    # Clean up repository after the test
    repo._states.clear()

    return {
        "sequential": result1,
        "parallel": result2
    }


async def main():
    print("Testing workflow engine components...")

    # Test basic components
    await test_sequential_execution()
    await test_parallel_execution()
    await test_repository()

    # Test workflow engine
    await test_workflow_engine()

    # Test different execution strategies
    await test_workflow_execution_strategies()

    print("\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(main())