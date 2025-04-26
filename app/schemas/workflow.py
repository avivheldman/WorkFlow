from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any, Optional
from enum import Enum
import uuid
from datetime import datetime

class ExecutionType(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class TaskDefinition(BaseModel):
    name: str
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class StepDefinition(BaseModel):
    execution_type: ExecutionType
    tasks: List[TaskDefinition]


class WorkflowDefinition(BaseModel):
    name: str
    steps: List[StepDefinition]


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TaskState(BaseModel):
    name: str
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[bool] = None


class StepState(BaseModel):
    execution_type: ExecutionType
    tasks: Dict[str, TaskState] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING


class WorkflowState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    steps: Dict[int, StepState] = Field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())