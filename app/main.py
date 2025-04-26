import logging
from fastapi import FastAPI
from app.routers.workflow import router as workflow_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Workflow Engine API",
    description="A workflow engine that can execute tasks in sequence or parallel",
    version="0.1.0",
    docs_url="/docs",
)

app.include_router(workflow_router, prefix="/api")

@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)