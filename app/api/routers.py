from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict

from app.core.workflow import WorkflowEngine
from app.schemas.workflow import WorkflowDefinition
from app.core.repository import RedisStateRepository, InMemoryStateRepository

router = APIRouter()


def get_workflow_engine():
    """Get a workflow engine with repository"""
    try:
        # Try Redis first
        repo = RedisStateRepository()
        return WorkflowEngine(repo)
    except Exception:
        # Fall back to in-memory
        repo = InMemoryStateRepository()
        return WorkflowEngine(repo)


@router.post("/workflow")
async def create_workflow(
        definition: WorkflowDefinition,
        background_tasks: BackgroundTasks,
        engine: WorkflowEngine = Depends(get_workflow_engine)
):
    try:

        workflow = await engine.create_workflow(definition)
        background_tasks.add_task(engine.execute_workflow, workflow.id)

        return {
            "workflow_id": workflow.id,
            "status": workflow.status,
            "message": "Workflow started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}")
async def get_workflow(
        workflow_id: str,
        engine: WorkflowEngine = Depends(get_workflow_engine)
):
    workflow = await engine.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow