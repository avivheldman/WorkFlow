import asyncio
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


async def main():
    print("Testing workflow engine components...")
    await test_sequential_execution()
    await test_parallel_execution()
    print("\nAll tests completed!")
if __name__ == "__main__":
    asyncio.run(main())