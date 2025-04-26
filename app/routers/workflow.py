from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List

from app.core.workflow import WorkflowEngine
from app.schemas.workflow import WorkflowDefinition, WorkflowState
from app.core.repository import RedisStateRepository, InMemoryStateRepository

router = APIRouter()

def get_workflow_engine():
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
    workflow = await engine.get_workflow_state(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

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
    try:
        return await engine.get_all_workflows()
    except Exception as e:
        import traceback
        print(f"Error in get_all_workflows endpoint: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")