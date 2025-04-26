"""
Workflow router module for handling workflow API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Callable, Awaitable
import logging

from app.core.workflow import WorkflowEngine
from app.schemas.workflow import WorkflowDefinition, WorkflowState
from app.core.repository_factory import RepositoryFactory
from app.core.repository import StateRepository

logger = logging.getLogger(__name__)
router = APIRouter(tags=["workflows"])

# Global repository instance to avoid recreating it for each request
_repository = None

async def get_repository() -> StateRepository:
    """
    Get the repository instance, initializing it if needed.
    """
    global _repository
    if _repository is None:
        _repository = await RepositoryFactory.get_repository()
    return _repository

async def get_workflow_engine() -> WorkflowEngine:
    """
    Dependency that provides a WorkflowEngine instance.
    Uses the repository provided by get_repository().
    """
    repo = await get_repository()
    return WorkflowEngine(repo)


@router.post(
    "/workflow",
    status_code=202,
    summary="Create a new workflow",
    description="Creates a new workflow based on the provided definition and executes it"
)
async def create_workflow(
        definition: WorkflowDefinition,
        background_tasks: BackgroundTasks,
        engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Create and execute a new workflow.

    Args:
        definition: The workflow definition
        background_tasks: FastAPI background tasks
        engine: The workflow engine

    Returns:
        Dict with workflow_id, status and message
    """
    try:
        logger.info(f"Creating workflow with name: {definition.name}")
        workflow = await engine.create_workflow(definition)
        logger.info(f"Created workflow with ID: {workflow.id}")

        # Execute workflow in background
        background_tasks.add_task(engine.execute_workflow, workflow.id)
        logger.info(f"Added workflow execution to background tasks: {workflow.id}")

        return {
            "workflow_id": workflow.id,
            "status": workflow.status,
            "message": "Workflow created and execution started"
        }
    except Exception as e:
        logger.error(f"Error creating workflow: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/workflow/{workflow_id}",
    response_model=WorkflowState,
    summary="Get workflow by ID",
    description="Retrieves a specific workflow by its ID"
)
async def get_workflow(
        workflow_id: str,
        engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Get a workflow by ID.

    Args:
        workflow_id: The ID of the workflow to retrieve
        engine: The workflow engine

    Returns:
        The workflow state

    Raises:
        HTTPException: If the workflow is not found
    """
    logger.info(f"Getting workflow with ID: {workflow_id}")
    workflow = await engine.get_workflow_state(workflow_id)

    if not workflow:
        logger.warning(f"Workflow not found: {workflow_id}")
        raise HTTPException(status_code=404, detail="Workflow not found")

    logger.info(f"Found workflow: {workflow.name} (status: {workflow.status})")
    return workflow


@router.get(
    "/workflows",
    response_model=List[WorkflowState],
    summary="Get all workflows",
    description="Retrieves all workflows in the system"
)
async def get_all_workflows(
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Get all workflows.

    Args:
        engine: The workflow engine

    Returns:
        List of workflow states
    """
    try:
        logger.info("Getting all workflows")
        workflows = await engine.get_all_workflows()
        logger.info(f"Found {len(workflows)} workflows")
        return workflows
    except Exception as e:
        logger.error(f"Error getting all workflows: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")