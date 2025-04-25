from typing import Dict, Any, Optional
import uuid
from datetime import datetime

from app.schemas.workflow import (
    WorkflowDefinition, WorkflowState, StepState, TaskState, WorkflowStatus, TaskStatus
)
from app.core.repository import StateRepository


class WorkflowFactory:
    def __init__(self, state_repository: StateRepository):
        self.state_repository = state_repository

    async def create_workflow(self, workflow_def: WorkflowDefinition) -> WorkflowState:
        workflow_id = str(uuid.uuid4())
        workflow_state = WorkflowState(
            id=workflow_id,
            name=workflow_def.name,
            status=WorkflowStatus.PENDING,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        # Initialize steps
        for i, step_def in enumerate(workflow_def.steps):
            step_state = StepState(
                execution_type=step_def.execution_type,
                status=TaskStatus.PENDING
            )

            # Initialize tasks
            for task_def in step_def.tasks:
                task_state = TaskState(
                    name=task_def.name,
                    status=TaskStatus.PENDING
                )
                step_state.tasks[task_def.name] = task_state

            workflow_state.steps[i] = step_state

        # Save initial state
        await self.state_repository.save_workflow_state(workflow_id, workflow_state.dict())

        return workflow_state