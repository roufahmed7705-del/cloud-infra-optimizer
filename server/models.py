"""
Cloud Infrastructure Optimizer Environment Models

Typed Pydantic models for the OpenEnv specification.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class VMConfig(BaseModel):
    """Virtual Machine configuration."""
    instance_type: str = Field(..., description="Instance type (t2.micro, t2.small, m5.large, etc.)")
    count: int = Field(default=1, ge=1, le=100, description="Number of instances")
    cpu_cores: int = Field(..., description="CPU cores per instance")
    memory_gb: int = Field(..., description="Memory in GB per instance")
    hourly_cost: float = Field(..., description="Hourly cost per instance in USD")


class DatabaseConfig(BaseModel):
    """Database configuration."""
    engine: str = Field(..., description="Database engine (postgres, mysql, mongodb)")
    instance_size: str = Field(..., description="Instance size (small, medium, large)")
    replicas: int = Field(default=1, ge=1, le=5, description="Number of replicas")
    storage_gb: int = Field(default=100, ge=10, le=1000, description="Storage in GB")
    hourly_cost: float = Field(..., description="Hourly cost in USD")


class InfrastructureState(BaseModel):
    """Current infrastructure state."""
    web_servers: VMConfig
    app_servers: VMConfig
    database: DatabaseConfig
    load_balancer_active: bool = Field(default=True, description="Is load balancer active")
    total_monthly_cost: float = Field(description="Estimated monthly cost in USD")
    uptime_percentage: float = Field(ge=0, le=100, description="Current uptime percentage")
    response_time_ms: float = Field(ge=0, description="Average response time in milliseconds")
    error_rate: float = Field(ge=0, le=1, description="Error rate (0-1)")


class CloudInfraAction(BaseModel):
    """Action to take in the environment."""
    action_type: str = Field(..., description="Type of action: scale_up, scale_down, change_instance, add_replica, remove_replica, failover")
    target: str = Field(..., description="Target component: web_servers, app_servers, database")
    value: Optional[int] = Field(default=None, description="New value (count, replicas, etc.)")
    instance_type: Optional[str] = Field(default=None, description="New instance type (for change_instance)")


class CloudInfraObservation(BaseModel):
    """Observation returned after each step."""
    infrastructure_state: InfrastructureState
    task_progress: float = Field(ge=0, le=1, description="Progress towards task completion (0-1)")
    reward: float = Field(description="Reward for this step")
    done: bool = Field(default=False, description="Whether episode is done")
    info: Dict[str, Any] = Field(default_factory=dict, description="Additional information")
    message: str = Field(default="", description="Human-readable message about the action")


class CloudInfraState(BaseModel):
    """Current state of the environment."""
    episode_id: str
    step_count: int
    infrastructure_state: InfrastructureState
    task_type: str = Field(description="Task type: easy, medium, hard")
    task_description: str
    max_steps: int
