# Cloud Infrastructure Optimizer OpenEnv

A real-world **OpenEnv** environment for managing and optimizing cloud infrastructure resources. This environment simulates realistic cloud infrastructure management scenarios with three progressive tasks: scaling, cost optimization, and failure recovery.

## Overview

The Cloud Infrastructure Optimizer is a fully OpenEnv-compliant environment that challenges AI agents to make intelligent decisions about cloud resource allocation. The environment includes:

- **Typed Pydantic models** for Action, Observation, and State following the OpenEnv specification
- **Three progressive tasks** with varying difficulty levels (easy, medium, hard)
- **Meaningful reward functions** that provide partial progress signals throughout episodes
- **Realistic infrastructure simulation** with web servers, app servers, databases, and load balancers
- **FastAPI server** for HTTP-based interaction
- **Docker deployment** ready for Hugging Face Spaces

## Quick Start

### Prerequisites

- Python 3.8+
- Docker (for deployment)
- OpenAI API key (for baseline inference)

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server**:
   ```bash
   python -m uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Test the environment**:
   ```bash
   curl -X POST http://localhost:8000/reset -H "Content-Type: application/json" -d '{"task_type": "easy"}'
   ```

### Docker Deployment

1. **Build the Docker image**:
   ```bash
   docker build -t cloud-infra-optimizer:latest .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 cloud-infra-optimizer:latest
   ```

3. **Deploy to Hugging Face Spaces**:
   - Create a new Space on Hugging Face
   - Connect your Git repository
   - Set the Docker runtime
   - The space will automatically deploy using the provided `Dockerfile` and `openenv.yaml`

## Environment Specification

### API Endpoints

The environment exposes three core OpenEnv endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Reset the environment and start a new episode |
| `/step` | POST | Execute an action and receive observation |
| `/state` | GET | Get the current environment state |
| `/health` | GET | Health check endpoint |

### Action Space

Actions are JSON objects with the following structure:

```json
{
  "action_type": "scale_up | scale_down | change_instance | add_replica | remove_replica | failover",
  "target": "web_servers | app_servers | database",
  "value": 5,
  "instance_type": "t2.micro | t2.small | m5.large | ..."
}
```

### Observation Space

Observations contain infrastructure state, task progress, and reward:

```json
{
  "infrastructure_state": {
    "web_servers": {"instance_type": "t2.micro", "count": 2, ...},
    "app_servers": {"instance_type": "t2.small", "count": 2, ...},
    "database": {"engine": "postgres", "instance_size": "small", ...},
    "load_balancer_active": true,
    "total_monthly_cost": 1500.0,
    "uptime_percentage": 95.0,
    "response_time_ms": 150.0,
    "error_rate": 0.02
  },
  "task_progress": 0.0,
  "reward": 0.0,
  "done": false,
  "info": {...},
  "message": "Environment reset. Task: ..."
}
```

## Tasks

### Task 1: Easy - Traffic Spike Response

**Objective**: Scale web servers to handle a traffic spike

- **Initial State**: 2 web servers, 95% uptime
- **Goal**: Scale to 5+ web servers while maintaining 99%+ uptime
- **Max Steps**: 20
- **Reward**: +5 per additional server, +100 bonus for completion

**Actions**: Use `scale_up` on `web_servers`

### Task 2: Medium - Cost Optimization

**Objective**: Reduce infrastructure costs while maintaining performance

- **Initial State**: 4 web servers, 4 app servers, 2 DB replicas (~$5000/month)
- **Goal**: Reduce cost to <$3000/month while maintaining 99% uptime and <150ms response time
- **Max Steps**: 30
- **Reward**: Cost savings per step, +100 bonus for completion

**Actions**: Use `change_instance` to downgrade instance types

### Task 3: Hard - Failure Recovery

**Objective**: Restore service from critical failure

- **Initial State**: Load balancer down, 20% uptime, 5000ms response time
- **Goal**: Restore to 99.5% uptime and <200ms response time
- **Max Steps**: 40
- **Reward**: +50 for failover, +20 per replica, +100 bonus for completion

**Actions**: Use `failover` to restore load balancer, `add_replica` for database resilience

## Reward Functions

The environment provides meaningful rewards throughout episodes:

- **Partial Progress Signals**: Rewards reflect progress toward task completion, not just binary success/failure
- **Action Penalties**: Invalid or counterproductive actions receive negative rewards
- **Completion Bonus**: +100 reward for successfully completing a task
- **Cost Awareness**: Rewards consider both performance and cost efficiency

## Example Usage

### Python Client

```python
import requests
import json

# Reset environment
response = requests.post(
    "http://localhost:8000/reset",
    json={"task_type": "easy"}
)
observation = response.json()

# Execute action
action = {
    "action_type": "scale_up",
    "target": "web_servers",
    "value": 5
}
response = requests.post(
    "http://localhost:8000/step",
    json=action
)
observation = response.json()

# Get current state
response = requests.get("http://localhost:8000/state")
state = response.json()
```

### Baseline Inference

Run the baseline agent (requires OpenAI API key):

```bash
export OPENAI_API_KEY="your-api-key"
python baseline_inference.py --task easy
python baseline_inference.py --task all  # Run all tasks
```

The baseline script will:
1. Reset the environment for each task
2. Use Claude to generate actions based on infrastructure state
3. Execute actions and collect rewards
4. Save results to `baseline_results.json`

## Project Structure

```
cloud_infra_env/
├── server/
│   ├── models.py           # Pydantic models (Action, Observation, State)
│   ├── environment.py      # Core environment logic
│   ├── app.py             # FastAPI server
│   └── __init__.py
├── openenv.yaml           # OpenEnv specification
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image definition
├── baseline_inference.py # Baseline agent script
└── README.md            # This file
```

## Model Definitions

### Action Model

```python
class CloudInfraAction(BaseModel):
    action_type: str  # scale_up, scale_down, change_instance, add_replica, remove_replica, failover
    target: str       # web_servers, app_servers, database
    value: Optional[int]
    instance_type: Optional[str]
```

### Observation Model

```python
class CloudInfraObservation(BaseModel):
    infrastructure_state: InfrastructureState
    task_progress: float      # 0.0 to 1.0
    reward: float
    done: bool
    info: Dict[str, Any]
    message: str
```

### State Model

```python
class CloudInfraState(BaseModel):
    episode_id: str
    step_count: int
    infrastructure_state: InfrastructureState
    task_type: str
    task_description: str
    max_steps: int
```

## Deployment to Hugging Face Spaces

1. Create a new Space on Hugging Face Hub
2. Choose "Docker" as the runtime
3. Connect your GitHub repository containing this code
4. The Space will automatically:
   - Build the Docker image using the provided `Dockerfile`
   - Deploy the FastAPI server
   - Expose the OpenEnv API at `/api/`

## Validation

To validate the environment against the OpenEnv specification:

```bash
openenv validate openenv.yaml
```

## Performance Benchmarks

Expected baseline performance (using Claude 3.5 Sonnet):

| Task | Avg Reward | Success Rate | Avg Steps |
|------|-----------|--------------|-----------|
| Easy | 45-60 | 70-80% | 15-18 |
| Medium | 30-50 | 40-60% | 20-28 |
| Hard | 50-80 | 30-50% | 25-35 |

## Extending the Environment

To add new tasks or features:

1. **Add new task types** in `environment.py`:
   - Define initial infrastructure state
   - Implement reward logic in `_process_action()`
   - Update `_update_infrastructure_state()` for state transitions

2. **Add new actions**:
   - Extend `CloudInfraAction` model in `models.py`
   - Implement action handling in `_process_action()`

3. **Modify reward functions**:
   - Edit reward calculation in `_process_action()`
   - Adjust task progress calculation

## Troubleshooting

### Server won't start
- Check that port 8000 is not in use: `lsof -i :8000`
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Docker build fails
- Ensure Docker is installed and running
- Check that all files are in the correct locations
- Verify Python version compatibility

### API requests fail
- Ensure server is running: `curl http://localhost:8000/health`
- Check request format matches API specification
- Review server logs for error details

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

## References

- [OpenEnv Specification](https://github.com/meta-pytorch/OpenEnv)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Gymnasium Documentation](https://gymnasium.farama.org/)
