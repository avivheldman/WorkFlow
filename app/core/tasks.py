from abc import ABC, abstractmethod
import uuid
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Union
import asyncio


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Task(ABC):
    def __init__(self, name: str):
        self.name = name
        self.status = TaskStatus.PENDING

    @abstractmethod
    async def execute(self) -> bool:
        pass

    def get_status(self) -> TaskStatus:
        return self.status

    def set_status(self, status: TaskStatus) -> None:
        self.status = status


class TaskA(Task):
    def __init__(self):
        super().__init__("task_a")

    async def execute(self) -> bool:
        self.set_status(TaskStatus.RUNNING)
        print("Running task A")
        # Simulate some work
        await asyncio.sleep(1)
        self.set_status(TaskStatus.SUCCEEDED)
        return True


class TaskB(Task):
    def __init__(self):
        super().__init__("task_b")

    async def execute(self) -> bool:
        self.set_status(TaskStatus.RUNNING)
        print("Running task B")
        # Simulate some work
        await asyncio.sleep(2)
        self.set_status(TaskStatus.SUCCEEDED)
        return True


class TaskC(Task):
    def __init__(self):
        super().__init__("task_c")

    async def execute(self) -> bool:
        self.set_status(TaskStatus.RUNNING)
        print("Running task C")
        # Simulate some work
        await asyncio.sleep(1.5)
        self.set_status(TaskStatus.SUCCEEDED)
        return True