"""
FastAPI server for Cloud Infrastructure Optimizer OpenEnv Environment
"""

from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from .models import CloudInfraAction, CloudInfraObservation, CloudInfraState
from .environment import CloudInfraEnvironment

# Global environment instance
env: Optional[CloudInfraEnvironment] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI."""
    global env
    env = CloudInfraEnvironment()
    print("Environment initialized")
    yield
    print("Environment shutdown")


app = FastAPI(
    title="Cloud Infrastructure Optimizer OpenEnv",
    description="A real-world OpenEnv environment for managing cloud infrastructure",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/reset")
async def reset(
    seed: Optional[int] = None,
    episode_id: Optional[str] = None,
    task_type: str = "easy",
) -> CloudInfraObservation:
    """Reset the environment."""
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    observation = env.reset(seed=seed, episode_id=episode_id, task_type=task_type)
    return observation


@app.post("/step")
async def step(action: CloudInfraAction, timeout_s: Optional[float] = None) -> CloudInfraObservation:
    """Execute one step in the environment."""
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    observation = env.step(action, timeout_s=timeout_s)
    return observation


@app.get("/state")
async def state() -> CloudInfraState:
    """Get current state."""
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    return env.state_fn()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Cloud Infrastructure Optimizer OpenEnv",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "reset": "/reset",
            "step": "/step",
            "state": "/state",
            "docs": "/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
