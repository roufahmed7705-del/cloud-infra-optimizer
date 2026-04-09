"""
Cloud Infrastructure Optimizer Environment

A real-world OpenEnv environment for managing cloud infrastructure.
"""

import random
import uuid
from typing import Optional, Tuple
from .models import (
    CloudInfraAction,
    CloudInfraObservation,
    CloudInfraState,
    DatabaseConfig,
    InfrastructureState,
    VMConfig,
)


class CloudInfraEnvironment:
    """Cloud Infrastructure Optimizer Environment."""

    def __init__(self):
        self.state: Optional[CloudInfraState] = None
        self.initial_state: Optional[InfrastructureState] = None
        self.task_type: str = "easy"
        self.episode_id: str = ""
        self.step_count: int = 0
        self.max_steps: int = 50

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_type: str = "easy",
        **kwargs
    ) -> CloudInfraObservation:
        """Reset the environment to initial state."""
        if seed is not None:
            random.seed(seed)

        self.episode_id = episode_id or str(uuid.uuid4())
        self.task_type = task_type
        self.step_count = 0

        # Initialize infrastructure based on task
        if task_type == "easy":
            # Task 1: Scale up web servers to handle traffic spike
            self.initial_state = InfrastructureState(
                web_servers=VMConfig(
                    instance_type="t2.micro",
                    count=2,
                    cpu_cores=1,
                    memory_gb=1,
                    hourly_cost=0.012,
                ),
                app_servers=VMConfig(
                    instance_type="t2.small",
                    count=2,
                    cpu_cores=1,
                    memory_gb=2,
                    hourly_cost=0.023,
                ),
                database=DatabaseConfig(
                    engine="postgres",
                    instance_size="small",
                    replicas=1,
                    storage_gb=100,
                    hourly_cost=0.25,
                ),
                load_balancer_active=True,
                total_monthly_cost=self._calculate_monthly_cost(
                    VMConfig(
                        instance_type="t2.micro",
                        count=2,
                        cpu_cores=1,
                        memory_gb=1,
                        hourly_cost=0.012,
                    ),
                    VMConfig(
                        instance_type="t2.small",
                        count=2,
                        cpu_cores=1,
                        memory_gb=2,
                        hourly_cost=0.023,
                    ),
                    DatabaseConfig(
                        engine="postgres",
                        instance_size="small",
                        replicas=1,
                        storage_gb=100,
                        hourly_cost=0.25,
                    ),
                ),
                uptime_percentage=95.0,
                response_time_ms=150.0,
                error_rate=0.02,
            )
            self.max_steps = 20
            task_description = "Traffic spike detected! Scale up web servers from 2 to at least 5 instances to maintain uptime above 99%."

        elif task_type == "medium":
            # Task 2: Optimize multi-tier app for budget
            self.initial_state = InfrastructureState(
                web_servers=VMConfig(
                    instance_type="m5.large",
                    count=4,
                    cpu_cores=2,
                    memory_gb=8,
                    hourly_cost=0.096,
                ),
                app_servers=VMConfig(
                    instance_type="m5.xlarge",
                    count=4,
                    cpu_cores=4,
                    memory_gb=16,
                    hourly_cost=0.192,
                ),
                database=DatabaseConfig(
                    engine="postgres",
                    instance_size="large",
                    replicas=2,
                    storage_gb=500,
                    hourly_cost=1.0,
                ),
                load_balancer_active=True,
                total_monthly_cost=self._calculate_monthly_cost(
                    VMConfig(
                        instance_type="m5.large",
                        count=4,
                        cpu_cores=2,
                        memory_gb=8,
                        hourly_cost=0.096,
                    ),
                    VMConfig(
                        instance_type="m5.xlarge",
                        count=4,
                        cpu_cores=4,
                        memory_gb=16,
                        hourly_cost=0.192,
                    ),
                    DatabaseConfig(
                        engine="postgres",
                        instance_size="large",
                        replicas=2,
                        storage_gb=500,
                        hourly_cost=1.0,
                    ),
                ),
                uptime_percentage=99.5,
                response_time_ms=100.0,
                error_rate=0.005,
            )
            self.max_steps = 30
            task_description = "Reduce monthly infrastructure cost from $5000 to under $3000 while maintaining 99% uptime and <150ms response time."

        else:  # hard
            # Task 3: Resolve cascading failure
            self.initial_state = InfrastructureState(
                web_servers=VMConfig(
                    instance_type="t2.small",
                    count=3,
                    cpu_cores=1,
                    memory_gb=2,
                    hourly_cost=0.023,
                ),
                app_servers=VMConfig(
                    instance_type="t2.medium",
                    count=2,
                    cpu_cores=2,
                    memory_gb=4,
                    hourly_cost=0.047,
                ),
                database=DatabaseConfig(
                    engine="postgres",
                    instance_size="medium",
                    replicas=1,
                    storage_gb=200,
                    hourly_cost=0.5,
                ),
                load_balancer_active=False,  # Failure condition
                total_monthly_cost=self._calculate_monthly_cost(
                    VMConfig(
                        instance_type="t2.small",
                        count=3,
                        cpu_cores=1,
                        memory_gb=2,
                        hourly_cost=0.023,
                    ),
                    VMConfig(
                        instance_type="t2.medium",
                        count=2,
                        cpu_cores=2,
                        memory_gb=4,
                        hourly_cost=0.047,
                    ),
                    DatabaseConfig(
                        engine="postgres",
                        instance_size="medium",
                        replicas=1,
                        storage_gb=200,
                        hourly_cost=0.5,
                    ),
                ),
                uptime_percentage=20.0,
                response_time_ms=5000.0,
                error_rate=0.95,
            )
            self.max_steps = 40
            task_description = "Critical failure: Load balancer down, uptime at 20%. Restore service to 99.5% uptime and <200ms response time. Add database replicas and fix load balancer."

        self.state = CloudInfraState(
            episode_id=self.episode_id,
            step_count=0,
            infrastructure_state=self.initial_state,
            task_type=task_type,
            task_description=task_description,
            max_steps=self.max_steps,
        )

        return CloudInfraObservation(
            infrastructure_state=self.state.infrastructure_state,
            task_progress=0.0,
            reward=0.0,
            done=False,
            info={
                "episode_id": self.episode_id,
                "task_type": task_type,
                "step": 0,
                "max_steps": self.max_steps,
            },
            message=f"Environment reset. Task: {task_description}",
        )

    def step(
        self, action: CloudInfraAction, timeout_s: Optional[float] = None, **kwargs
    ) -> CloudInfraObservation:
        """Execute one step in the environment."""
        if self.state is None:
            raise RuntimeError("Environment not reset. Call reset() first.")

        self.step_count += 1
        self.state.step_count = self.step_count

        # Process action
        reward, message, done, task_progress = self._process_action(action)

        # Update state based on task progress
        self._update_infrastructure_state(task_progress)

        # Check if task is complete or max steps reached
        if task_progress >= 0.95 or self.step_count >= self.max_steps:
            done = True
            if task_progress >= 0.95:
                reward += 100.0  # Bonus for completing task

        return CloudInfraObservation(
            infrastructure_state=self.state.infrastructure_state,
            task_progress=task_progress,
            reward=reward,
            done=done,
            info={
                "episode_id": self.episode_id,
                "task_type": self.task_type,
                "step": self.step_count,
                "max_steps": self.max_steps,
            },
            message=message,
        )

    def state_fn(self) -> CloudInfraState:
        """Return current state."""
        if self.state is None:
            raise RuntimeError("Environment not reset. Call reset() first.")
        return self.state

    def _process_action(self, action: CloudInfraAction) -> Tuple[float, str, bool, float]:
        """Process an action and return reward, message, done, and task progress."""
        if self.state is None:
            raise RuntimeError("State not initialized")

        reward = 0.0
        message = ""
        done = False
        task_progress = 0.0

        if self.task_type == "easy":
            # Task: Scale web servers to 5+
            target_count = 5
            current_count = self.state.infrastructure_state.web_servers.count

            if action.action_type == "scale_up" and action.target == "web_servers":
                if action.value and action.value > current_count:
                    self.state.infrastructure_state.web_servers.count = action.value
                    reward = (action.value - current_count) * 5.0
                    message = f"Scaled web servers from {current_count} to {action.value}"
                    
                    # Update metrics
                    if action.value >= target_count:
                        self.state.infrastructure_state.uptime_percentage = 99.5
                        self.state.infrastructure_state.response_time_ms = 120.0
                        task_progress = min(1.0, action.value / target_count)
                else:
                    reward = -5.0
                    message = "Invalid scale_up action"
            else:
                reward = -1.0
                message = f"Wrong action type. Use 'scale_up' on 'web_servers'. Got {action.action_type} on {action.target}"

        elif self.task_type == "medium":
            # Task: Reduce cost while maintaining performance
            target_cost = 3000.0
            current_cost = self.state.infrastructure_state.total_monthly_cost
            uptime = self.state.infrastructure_state.uptime_percentage
            response_time = self.state.infrastructure_state.response_time_ms

            if action.action_type == "change_instance":
                if action.target == "web_servers" and action.instance_type:
                    # Simulate downgrading instance type
                    cost_reduction = current_cost * 0.1
                    self.state.infrastructure_state.total_monthly_cost = max(
                        target_cost, current_cost - cost_reduction
                    )
                    reward = cost_reduction / 100.0
                    message = f"Changed web server instance type to {action.instance_type}"

                    # Check constraints
                    if uptime >= 99.0 and response_time <= 150.0:
                        task_progress = 1.0 - (self.state.infrastructure_state.total_monthly_cost / 5000.0)
                    else:
                        reward -= 10.0
                        message += " (Performance degraded!)"
                else:
                    reward = -2.0
                    message = "Invalid change_instance action"
            else:
                reward = -1.0
                message = f"Use 'change_instance' action for cost optimization"

        else:  # hard
            # Task: Restore service from failure
            if not self.state.infrastructure_state.load_balancer_active:
                if action.action_type == "failover":
                    self.state.infrastructure_state.load_balancer_active = True
                    self.state.infrastructure_state.uptime_percentage = 85.0
                    reward = 50.0
                    message = "Load balancer restored"
                elif action.action_type == "add_replica" and action.target == "database":
                    if action.value and action.value > self.state.infrastructure_state.database.replicas:
                        self.state.infrastructure_state.database.replicas = action.value
                        reward = 20.0 * (action.value - 1)
                        message = f"Added database replicas. Now {action.value} replicas"
                else:
                    reward = -2.0
                    message = "Use 'failover' or 'add_replica' actions"
            else:
                reward = -1.0
                message = "Load balancer already active"

            # Calculate progress
            uptime = self.state.infrastructure_state.uptime_percentage
            response_time = self.state.infrastructure_state.response_time_ms
            if uptime >= 99.5 and response_time <= 200.0:
                task_progress = 1.0
            else:
                task_progress = (uptime / 99.5) * 0.5 + min(1.0, (200.0 / response_time)) * 0.5

        return reward, message, done, task_progress

    def _update_infrastructure_state(self, task_progress: float) -> None:
        """Update infrastructure state based on task progress."""
        if self.state is None:
            return

        # Simulate gradual improvement as task progresses
        if self.task_type == "easy":
            target_uptime = 99.5
            current_uptime = self.state.infrastructure_state.uptime_percentage
            self.state.infrastructure_state.uptime_percentage = current_uptime + (
                target_uptime - current_uptime
            ) * 0.1
        elif self.task_type == "medium":
            # Cost optimization
            target_cost = 3000.0
            current_cost = self.state.infrastructure_state.total_monthly_cost
            self.state.infrastructure_state.total_monthly_cost = current_cost - (
                current_cost - target_cost
            ) * 0.05
        else:  # hard
            # Failure recovery
            if self.state.infrastructure_state.load_balancer_active:
                self.state.infrastructure_state.uptime_percentage = min(
                    99.5,
                    self.state.infrastructure_state.uptime_percentage + 10.0,
                )
                self.state.infrastructure_state.response_time_ms = max(
                    100.0,
                    self.state.infrastructure_state.response_time_ms * 0.9,
                )

    @staticmethod
    def _calculate_monthly_cost(web_vms: VMConfig, app_vms: VMConfig, db: DatabaseConfig) -> float:
        """Calculate estimated monthly cost."""
        web_cost = web_vms.count * web_vms.hourly_cost * 730  # 730 hours/month
        app_cost = app_vms.count * app_vms.hourly_cost * 730
        db_cost = db.hourly_cost * 730
        return web_cost + app_cost + db_cost
