from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from app.core.execution import SequentialExecution, ParallelExecution
from app.core.repository import StateRepository
from app.core.task_factory import TaskFactory
from app.schemas.workflow import ExecutionType, WorkflowDefinition, WorkflowState, WorkflowStatus, TaskStatus
from app.core.workflow_factory import WorkflowFactory
logger = logging.getLogger(__name__)


class WorkflowEngine:
    def __init__(self, state_repository: StateRepository):
        self.state_repository = state_repository
        self.workflow_factory = WorkflowFactory(state_repository)

        self.task_factory = TaskFactory()
        self.execution_strategies = {
            ExecutionType.SEQUENTIAL: SequentialExecution(),
            ExecutionType.PARALLEL: ParallelExecution()
        }
        logger.info("Initialized WorkflowEngine")

    async def create_workflow(self, workflow_def: WorkflowDefinition) -> WorkflowState:
        return await self.workflow_factory.create_workflow(workflow_def)

    async def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        state_dict = await self.state_repository.get_workflow_state(workflow_id)
        if not state_dict:
            return None
        return WorkflowState(**state_dict)

    async def execute_workflow(self, workflow_id: str) -> WorkflowState:
        """
        Execute a workflow.
        Args:
            workflow_id: The ID of the workflow to execute
        Returns:
            The updated workflow state
        Raises:
            ValueError: If the workflow is not found
        """
        state_dict = await self.state_repository.get_workflow_state(workflow_id)
        if not state_dict:
            logger.error(f"Workflow not found: {workflow_id}")
            raise ValueError(f"Workflow with ID {workflow_id} not found")

        workflow_state = WorkflowState(**state_dict)
        workflow_state.status = WorkflowStatus.RUNNING
        workflow_state.updated_at = datetime.now().isoformat()

        logger.info(f"Starting execution of workflow {workflow_id} ({workflow_state.name})")
        logger.info(f"Workflow has the following steps: {list(workflow_state.steps.keys())}")

        await self.state_repository.save_workflow_state(workflow_id, workflow_state.dict())
        step_indices = sorted([k for k in workflow_state.steps.keys()])
        logger.info(f"Steps to execute in order: {step_indices}")

        for step_idx in step_indices:
            logger.info(f"Processing step {step_idx}")

            # Access step using string key
            if step_idx not in workflow_state.steps:
                logger.error(f"Step {step_idx} not found in workflow steps: {list(workflow_state.steps.keys())}")
                workflow_state.status = WorkflowStatus.FAILED
                workflow_state.updated_at = datetime.now().isoformat()
                await self.state_repository.save_workflow_state(workflow_id, workflow_state.dict())
                return workflow_state

            step = workflow_state.steps[step_idx]
            step.status = TaskStatus.RUNNING

            logger.info(f"Executing step {step_idx} with execution type {step.execution_type}")
            await self.state_repository.save_workflow_state(workflow_id, workflow_state.dict())
            success = await self._execute_step(workflow_id, workflow_state, step_idx, step)

            if not success:
                workflow_state.status = WorkflowStatus.FAILED
                workflow_state.updated_at = datetime.now().isoformat()
                await self.state_repository.save_workflow_state(workflow_id, workflow_state.dict())
                logger.warning(f"Workflow {workflow_id} failed at step {step_idx}")
                return workflow_state

        workflow_state.status = WorkflowStatus.SUCCEEDED
        workflow_state.updated_at = datetime.now().isoformat()
        logger.info(f"Workflow {workflow_id} completed successfully")
        await self.state_repository.save_workflow_state(workflow_id, workflow_state.dict())

        return workflow_state

    async def _execute_step(self, workflow_id: str, workflow_state: WorkflowState, step_idx: str, step: Any) -> bool:
        """
        Execute a workflow step.

        Args:
            workflow_id: The ID of the workflow
            workflow_state: The current workflow state
            step_idx: The index of the step (as a string)
            step: The step to execute

        Returns:
            bool: True if the step succeeded, False otherwise
        """
        try:
            logger.debug(f"Step {step_idx} contains tasks: {list(step.tasks.keys())}")

            if not step.tasks:
                logger.error(f"Step {step_idx} has no tasks")
                return False

            tasks = []
            task_names = list(step.tasks.keys())

            for task_name in task_names:
                try:
                    logger.debug(f"Creating task {task_name}")
                    task = self.task_factory.create_task(task_name)
                    tasks.append(task)
                except Exception as e:
                    logger.error(f"Failed to create task {task_name}: {e}")
                    return False

            execution_strategy = self.execution_strategies[step.execution_type]
            logger.debug(f"Using {step.execution_type} execution strategy for step {step_idx}")
            try:
                results = await execution_strategy.execute(tasks)
                logger.debug(f"Execution results: {results}")
            except Exception as e:
                logger.error(f"Error during task execution: {e}", exc_info=True)
                return False

            # Update task states
            step_success = True
            for task, result in zip(tasks, results.values()):
                task_name = task.name
                logger.debug(f"Updating task state for {task_name}: {result}")

                if task_name in step.tasks:
                    task_state = step.tasks[task_name]
                    task_state.status = TaskStatus.SUCCEEDED if result else TaskStatus.FAILED
                    task_state.result = result

                    if not result:
                        step_success = False
                else:
                    logger.error(f"Task {task_name} not found in step.tasks")
                    step_success = False

            step.status = TaskStatus.SUCCEEDED if step_success else TaskStatus.FAILED
            logger.info(f"Step {step_idx} completed with status: {step.status}")

            # Save state after step execution
            await self.state_repository.save_workflow_state(workflow_id, workflow_state.dict())
            return step_success
        except Exception as e:
            logger.error(f"Unexpected error executing step {step_idx}: {e}", exc_info=True)
            step.status = TaskStatus.FAILED
            await self.state_repository.save_workflow_state(workflow_id, workflow_state.dict())
            return False

    async def get_all_workflows(self) -> List[WorkflowState]:
        try:
            state_dicts = await self.state_repository.get_all_workflow_states()
            logger.debug(f"Retrieved {len(state_dicts)} workflow states")
            return [WorkflowState(**state_dict) for state_dict in state_dicts]
        except Exception as e:
            logger.error(f"Error in get_all_workflows: {e}", exc_info=True)
            raise