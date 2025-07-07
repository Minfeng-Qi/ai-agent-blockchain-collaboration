"""
Main application module for the Agent Learning System API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from app.config import PROJECT_NAME, DESCRIPTION, VERSION, CORS_ORIGINS
from app.routers import agents, tasks, learning

# Create FastAPI app
app = FastAPI(
    title=PROJECT_NAME,
    description=DESCRIPTION,
    version=VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(learning.router, prefix="/learning", tags=["learning"])


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=PROJECT_NAME,
        version=VERSION,
        description=DESCRIPTION,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/", tags=["status"])
async def root():
    """
    Root endpoint to check API status.
    """
    return JSONResponse(
        content={
            "status": "online",
            "name": PROJECT_NAME,
            "version": VERSION,
            "message": "Welcome to the Agent Learning System API",
        }
    )


@app.get("/health", tags=["status"])
async def health_check():
    """
    Health check endpoint.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "services": {
                "api": "up",
                "blockchain": "up",  # This should be dynamically checked
            },
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)