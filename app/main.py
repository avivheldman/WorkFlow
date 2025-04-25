from fastapi import FastAPI
from app.api.routers import router

# Create FastAPI app with metadata for Swagger
app = FastAPI(
    title="Workflow Engine API",
    description="A simple workflow engine that can execute tasks in sequence or parallel",
    version="0.1.0",
    docs_url="/docs",
)


app.include_router(router)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)