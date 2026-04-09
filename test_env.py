#!/usr/bin/env python3
"""Quick test of the Cloud Infrastructure Optimizer environment."""

from server.environment import CloudInfraEnvironment
from server.models import CloudInfraAction

# Create environment
env = CloudInfraEnvironment()

# Test Easy Task
print("=" * 60)
print("Testing Easy Task: Traffic Spike Response")
print("=" * 60)

obs = env.reset(task_type="easy")
print(f"✓ Environment reset")
print(f"  Task: {obs.info['task_type']}")
print(f"  Message: {obs.message}")
print(f"  Initial uptime: {obs.infrastructure_state.uptime_percentage:.1f}%\n")

# Execute a scale_up action
action = CloudInfraAction(
    action_type="scale_up",
    target="web_servers",
    value=5,
)
obs = env.step(action)
print(f"✓ Executed action: scale_up web_servers to 5")
print(f"  Reward: {obs.reward:.2f}")
print(f"  Progress: {obs.task_progress*100:.1f}%")
print(f"  Message: {obs.message}")
print(f"  New uptime: {obs.infrastructure_state.uptime_percentage:.1f}%\n")

# Test Medium Task
print("=" * 60)
print("Testing Medium Task: Cost Optimization")
print("=" * 60)

obs = env.reset(task_type="medium")
print(f"✓ Environment reset")
print(f"  Task: {obs.info['task_type']}")
print(f"  Initial cost: ${obs.infrastructure_state.total_monthly_cost:.2f}/month\n")

# Execute a change_instance action
action = CloudInfraAction(
    action_type="change_instance",
    target="web_servers",
    instance_type="t2.small",
)
obs = env.step(action)
print(f"✓ Executed action: change_instance web_servers to t2.small")
print(f"  Reward: {obs.reward:.2f}")
print(f"  Progress: {obs.task_progress*100:.1f}%")
print(f"  New cost: ${obs.infrastructure_state.total_monthly_cost:.2f}/month\n")

# Test Hard Task
print("=" * 60)
print("Testing Hard Task: Failure Recovery")
print("=" * 60)

obs = env.reset(task_type="hard")
print(f"✓ Environment reset")
print(f"  Task: {obs.info['task_type']}")
print(f"  Initial uptime: {obs.infrastructure_state.uptime_percentage:.1f}%")
print(f"  Load balancer active: {obs.infrastructure_state.load_balancer_active}\n")

# Execute a failover action
action = CloudInfraAction(
    action_type="failover",
    target="database",
)
obs = env.step(action)
print(f"✓ Executed action: failover")
print(f"  Reward: {obs.reward:.2f}")
print(f"  Progress: {obs.task_progress*100:.1f}%")
print(f"  Message: {obs.message}")
print(f"  New uptime: {obs.infrastructure_state.uptime_percentage:.1f}%")
print(f"  Load balancer active: {obs.infrastructure_state.load_balancer_active}\n")

print("=" * 60)
print("✓ All tests passed!")
print("=" * 60)
