"""
Workflow factory module for creating workflow instances.
"""
import uuid
from datetime import datetime
import logging

from app.schemas.workflow import (
    WorkflowDefinition, WorkflowState, StepState, TaskState,
    TaskStatus, WorkflowStatus
)
from app.core.repository import StateRepository

logger = logging.getLogger(__name__)


class WorkflowFactory:
    def __init__(self, repository: StateRepository):
        self.repository = repository
        logger.info("Initialized WorkflowFactory")

    async def create_workflow(self, definition: WorkflowDefinition) -> WorkflowState:
        workflow_id = str(uuid.uuid4())
        logger.info(f"Creating workflow with ID: {workflow_id}, name: {definition.name}")

        # Create workflow state
        workflow_state = WorkflowState(
            id=workflow_id,
            name=definition.name,
            status=WorkflowStatus.PENDING,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            steps={}  # Initialize with empty dict
        )

        # Create steps
        for i, step_def in enumerate(definition.steps):
            # Create step state
            step_state = StepState(
                execution_type=step_def.execution_type,
                status=TaskStatus.PENDING,
                tasks={}  # Initialize with empty dict
            )

            logger.debug(f"Creating step {i} with execution type: {step_def.execution_type}")

            # Create task states
            for task_def in step_def.tasks:
                task_state = TaskState(
                    name=task_def.name,
                    status=TaskStatus.PENDING
                )
                step_state.tasks[task_def.name] = task_state
                logger.debug(f"Added task {task_def.name} to step {i}")

            # Store step with string index
            workflow_state.steps[str(i)] = step_state

        # Save to repository
        await self.repository.save_workflow_state(workflow_id, workflow_state.dict())
        logger.info(f"Saved workflow {workflow_id} to repository")

        return workflow_state