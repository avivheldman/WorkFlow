from typing import List, Dict
from app.core.tasks import Task
from abc import ABC, abstractmethod
import asyncio
import logging

logger = logging.getLogger(__name__)


class Execution(ABC):
    @abstractmethod
    async def execute(self, tasks: List[Task]) -> Dict[str, bool]:
        pass


class SequentialExecution(Execution):
    async def execute(self, tasks: List[Task]) -> Dict[str, bool]:
        results = {}
        for task in tasks:
            logger.info(f"Sequentially executing task: {task.name}")
            try:
                result = await task.execute()
                results[task.name] = result
                logger.info(f"Task {task.name} completed with result: {result}")
                # If a task fails, stop execution
                if not result:
                    logger.warning(f"Task {task.name} failed, stopping sequential execution")
                    break
            except Exception as e:
                logger.error(f"Error executing task {task.name}: {e}")
                results[task.name] = False
                break
        return results


class ParallelExecution(Execution):
    async def execute(self, tasks: List[Task]) -> Dict[str, bool]:
        logger.info(f"Starting parallel execution of {len(tasks)} tasks")
        results = {}

        try:
            # Create tasks with explicit naming for better debugging
            pending_tasks = []
            for task in tasks:
                logger.debug(f"Adding task {task.name} to parallel execution")
                pending_tasks.append(task.execute())

            # Execute all tasks in parallel
            execution_results = await asyncio.gather(*pending_tasks, return_exceptions=True)

            # Process results
            for i, (task, result) in enumerate(zip(tasks, execution_results)):
                if isinstance(result, Exception):
                    logger.error(f"Task {task.name} failed with exception: {result}")
                    results[task.name] = False
                else:
                    logger.info(f"Task {task.name} completed with result: {result}")
                    results[task.name] = result
        except Exception as e:
            logger.error(f"Error during parallel execution: {e}")
            # Make sure all tasks have a result
            for task in tasks:
                if task.name not in results:
                    results[task.name] = False

        return results