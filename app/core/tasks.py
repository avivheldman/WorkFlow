from abc import ABC, abstractmethod
import uuid
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Union
import asyncio
import logging

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Task(ABC):
    def __init__(self, name: str):
        self.name = name
        self.status = TaskStatus.PENDING
        logger.debug(f"Initialized task: {name}")

    @abstractmethod
    async def execute(self) -> bool:
        pass

    def get_status(self) -> TaskStatus:
        return self.status

    def set_status(self, status: TaskStatus) -> None:
        logger.debug(f"Setting task {self.name} status to {status}")
        self.status = status


class TaskA(Task):
    def __init__(self):
        super().__init__("task_a")

    async def execute(self) -> bool:
        try:
            self.set_status(TaskStatus.RUNNING)
            logger.info("Running task A")
            # Simulate some work
            await asyncio.sleep(1)
            self.set_status(TaskStatus.SUCCEEDED)
            return True
        except Exception as e:
            logger.error(f"Error in task A: {e}")
            self.set_status(TaskStatus.FAILED)
            return False


class TaskB(Task):
    def __init__(self):
        super().__init__("task_b")

    async def execute(self) -> bool:
        try:
            self.set_status(TaskStatus.RUNNING)
            logger.info("Running task B")
            # Simulate some work
            await asyncio.sleep(2)
            self.set_status(TaskStatus.SUCCEEDED)
            return True
        except Exception as e:
            logger.error(f"Error in task B: {e}")
            self.set_status(TaskStatus.FAILED)
            return False


class TaskC(Task):
    def __init__(self):
        super().__init__("task_c")

    async def execute(self) -> bool:
        try:
            self.set_status(TaskStatus.RUNNING)
            logger.info("Running task C")
            # Simulate some work
            await asyncio.sleep(1.5)
            self.set_status(TaskStatus.SUCCEEDED)
            return True
        except Exception as e:
            logger.error(f"Error in task C: {e}")
            self.set_status(TaskStatus.FAILED)
            return False