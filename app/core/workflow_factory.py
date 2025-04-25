# app/core/workflow_factory.py
import uuid
from datetime import datetime

from app.schemas.workflow import (
    WorkflowDefinition, WorkflowState, StepState, TaskState,
    TaskStatus, WorkflowStatus
)
from app.core.repository import StateRepository


class WorkflowFactory:
    def __init__(self, repository: StateRepository):
        self.repository = repository

    async def create_workflow(self, definition: WorkflowDefinition) -> WorkflowState:
        workflow_id = str(uuid.uuid4())

        # Create workflow state
        workflow_state = WorkflowState(
            id=workflow_id,
            name=definition.name,
            status=WorkflowStatus.PENDING,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        # Create steps
        for i, step_def in enumerate(definition.steps):
            # Create step state
            step_state = StepState(
                execution_type=step_def.execution_type,
                status=TaskStatus.PENDING
            )

            # Create task states
            for task_def in step_def.tasks:
                task_state = TaskState(
                    name=task_def.name,
                    status=TaskStatus.PENDING
                )
                step_state.tasks[task_def.name] = task_state

            workflow_state.steps[i] = step_state

        # Save to repository
        await self.repository.save_workflow_state(workflow_id, workflow_state.dict())

        return workflow_state
