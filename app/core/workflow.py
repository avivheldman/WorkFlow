# app/core/workflow.py
from datetime import datetime
from typing import Optional,List

from app.core.execution import SequentialExecution, ParallelExecution
from app.core.repository import StateRepository
from app.core.task_factory import TaskFactory
from app.core.workflow_factory import WorkflowFactory
from app.schemas.workflow import ExecutionType, WorkflowDefinition, WorkflowState, WorkflowStatus, TaskStatus


class WorkflowEngine:
    def __init__(self, state_repository: StateRepository):
        self.state_repository = state_repository
        self.workflow_factory = WorkflowFactory(state_repository)
        self.task_factory = TaskFactory()
        self.execution_strategies = {
            ExecutionType.SEQUENTIAL: SequentialExecution(),
            ExecutionType.PARALLEL: ParallelExecution()
        }

    async def create_workflow(self, workflow_def: WorkflowDefinition) -> WorkflowState:
        return await self.workflow_factory.create_workflow(workflow_def)

    async def execute_workflow(self, workflow_id: str) -> WorkflowState:
        state_dict = await self.state_repository.get_workflow_state(workflow_id)
        if not state_dict:
            raise ValueError(f"Workflow with ID {workflow_id} not found")

        workflow_state = WorkflowState(**state_dict)
        workflow_state.status = WorkflowStatus.RUNNING
        workflow_state.updated_at = datetime.now().isoformat()

        # Execute steps in sequence
        for step_idx in sorted(workflow_state.steps.keys()):
            step = workflow_state.steps[step_idx]
            step.status = TaskStatus.RUNNING

            tasks = []
            for task_name in step.tasks:
                task = self.task_factory.create_task(task_name)
                tasks.append(task)

            # Get execution strategy
            execution_strategy = self.execution_strategies[step.execution_type]
            results = await execution_strategy.execute(tasks)

            # Update task states
            step_success = True
            for task_name, result in results.items():
                task_state = step.tasks[task_name]
                task_state.status = TaskStatus.SUCCEEDED if result else TaskStatus.FAILED
                task_state.result = result

                if not result:
                    step_success = False

            step.status = TaskStatus.SUCCEEDED if step_success else TaskStatus.FAILED

            await self.state_repository.save_workflow_state(workflow_id, workflow_state.dict())

            # If step failed, fail the workflow
            if not step_success:
                workflow_state.status = WorkflowStatus.FAILED
                await self.state_repository.save_workflow_state(workflow_id, workflow_state.dict())
                return workflow_state

        # All steps succeeded
        workflow_state.status = WorkflowStatus.SUCCEEDED
        workflow_state.updated_at = datetime.now().isoformat()
        await self.state_repository.save_workflow_state(workflow_id, workflow_state.dict())

        return workflow_state

    async def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        state_dict = await self.state_repository.get_workflow_state(workflow_id)
        if not state_dict:
            return None

        return WorkflowState(**state_dict)

    async def get_all_workflows(self) -> List[WorkflowState]:
        try:
            state_dicts = await self.repository.get_all_workflow_states()
            return [WorkflowState(**state_dict) for state_dict in state_dicts]
        except Exception as e:
            print(e)