from typing import List, Dict
from .tasks import Task
from abc import ABC, abstractmethod
import asyncio


class Execution(ABC):
    @abstractmethod
    async def execute(self, tasks: List[Task]) -> Dict[str, bool]:
        pass


class SequentialExecution(Execution):
    async def execute(self, tasks: List[Task]) -> Dict[str, bool]:
        results = {}
        for task in tasks:
            result = await task.execute()
            results[task.name] = result
            # If a task fails, stop execution
            if not result:
                break
        return results


class ParallelExecution(Execution):
    async def execute(self, tasks: List[Task]) -> Dict[str, bool]:
        pending_tasks = [task.execute() for task in tasks]
        results = await asyncio.gather(*pending_tasks)
        return {task.name: result for task, result in zip(tasks, results)}
