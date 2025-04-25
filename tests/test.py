import asyncio

from app.core.repository import InMemoryStateRepository, RedisStateRepository
from app.core.tasks import TaskA, TaskB, TaskC
from app.core.execution import ParallelExecution,SequentialExecution

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
    test_state = {"status": "running", "tasks": {"task_a": "succeeded"}}
    await memory_repo.save_workflow_state("test-workflow", test_state)

    retrieved_state = await memory_repo.get_workflow_state("test-workflow")

    print(f"Original state: {test_state}")
    print(f"Retrieved state: {retrieved_state}")
    try:
        redis_repo = RedisStateRepository()
        await redis_repo.save_workflow_state("test-workflow", test_state)
        redis_state = await redis_repo.get_workflow_state("test-workflow")
        print(f"Redis state: {redis_state}")
    except Exception as e:
        print(f"Redis test skipped: {str(e)}")


async def main():
    print("Testing workflow engine components...")
    await test_sequential_execution()
    await test_parallel_execution()
    await test_repository()
    print("\nAll tests completed!")
if __name__ == "__main__":
    asyncio.run(main())