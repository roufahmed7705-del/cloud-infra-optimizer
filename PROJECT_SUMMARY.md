# Cloud Infrastructure Optimizer - OpenEnv Hackathon Submission

## Executive Summary

This is a complete, production-ready **OpenEnv environment** for the Open Env Hackathon in Bangalore. The environment simulates real-world cloud infrastructure management scenarios with three progressive tasks that challenge AI agents to make intelligent resource allocation decisions.

## Key Features

### ✅ OpenEnv Specification Compliance

- **Typed Pydantic Models**: Full implementation of Action, Observation, and State models
- **Standard API**: `reset()`, `step()`, and `state()` endpoints following Gymnasium-style interface
- **HTTP Server**: FastAPI-based REST API for remote environment access
- **Docker Ready**: Dockerfile and configuration for Hugging Face Spaces deployment
- **Metadata**: Complete `openenv.yaml` with environment specification

### ✅ Real-World Task Simulation

The environment includes **three progressive tasks** that simulate authentic cloud infrastructure challenges:

| Task | Difficulty | Objective | Max Steps |
|------|-----------|-----------|-----------|
| **Easy** | Beginner | Scale web servers to handle traffic spike | 20 |
| **Medium** | Intermediate | Reduce costs while maintaining performance | 30 |
| **Hard** | Advanced | Recover from critical infrastructure failure | 40 |

### ✅ Meaningful Reward Functions

- **Partial Progress Signals**: Rewards reflect progress throughout episodes, not just binary success/failure
- **Action Penalties**: Invalid actions receive negative rewards to guide learning
- **Completion Bonus**: +100 reward for successfully completing tasks
- **Cost Awareness**: Rewards consider both performance metrics and operational costs

### ✅ Production-Ready Components

- **Baseline Inference Script**: Uses Claude 3.5 Sonnet to run agents against the environment
- **Comprehensive Documentation**: README, deployment guide, and API documentation
- **Testing Suite**: Included test script to validate environment functionality
- **Docker Deployment**: Ready for immediate deployment to Hugging Face Spaces

## Project Structure

```
cloud_infra_env/
├── server/
│   ├── models.py              # Pydantic models (Action, Observation, State)
│   ├── environment.py         # Core environment logic (3 tasks, reward functions)
│   ├── app.py                # FastAPI server with OpenEnv endpoints
│   └── __init__.py
├── openenv.yaml              # OpenEnv specification (spec_version: 1)
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker image for deployment
├── baseline_inference.py     # Baseline agent using Claude API
├── test_env.py              # Test script for validation
├── README.md                # Comprehensive documentation
├── DEPLOYMENT.md            # Deployment guide
└── PROJECT_SUMMARY.md       # This file
```

## Technical Specifications

### Environment Models

**Action Space**:
```python
{
  "action_type": "scale_up | scale_down | change_instance | add_replica | remove_replica | failover",
  "target": "web_servers | app_servers | database",
  "value": int,
  "instance_type": str
}
```

**Observation Space**:
```python
{
  "infrastructure_state": {
    "web_servers": VMConfig,
    "app_servers": VMConfig,
    "database": DatabaseConfig,
    "load_balancer_active": bool,
    "total_monthly_cost": float,
    "uptime_percentage": float,
    "response_time_ms": float,
    "error_rate": float
  },
  "task_progress": float,  # 0.0 to 1.0
  "reward": float,
  "done": bool,
  "info": dict,
  "message": str
}
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Reset environment for a task |
| `/step` | POST | Execute action and receive observation |
| `/state` | GET | Get current environment state |
| `/health` | GET | Health check |

### Task Specifications

#### Task 1: Easy - Traffic Spike Response
- **Initial State**: 2 web servers, 95% uptime, 150ms response time
- **Goal**: Scale to 5+ web servers while maintaining 99%+ uptime
- **Reward**: +5 per additional server, +100 completion bonus
- **Success Criteria**: 5+ web servers AND uptime ≥ 99%

#### Task 2: Medium - Cost Optimization
- **Initial State**: 4 web, 4 app servers, 2 DB replicas (~$1571/month)
- **Goal**: Reduce cost to <$3000/month while maintaining 99% uptime and <150ms response time
- **Reward**: Cost savings per step, +100 completion bonus
- **Success Criteria**: Cost < $3000 AND uptime ≥ 99% AND response time < 150ms

#### Task 3: Hard - Failure Recovery
- **Initial State**: Load balancer DOWN, 20% uptime, 5000ms response time
- **Goal**: Restore to 99.5% uptime and <200ms response time
- **Reward**: +50 for failover, +20 per replica, +100 completion bonus
- **Success Criteria**: Uptime ≥ 99.5% AND response time < 200ms

## Performance Benchmarks

Expected baseline performance using Claude 3.5 Sonnet:

| Task | Avg Reward | Success Rate | Avg Steps |
|------|-----------|--------------|-----------|
| Easy | 45-60 | 70-80% | 15-18 |
| Medium | 30-50 | 40-60% | 20-28 |
| Hard | 50-80 | 30-50% | 25-35 |

## Quick Start

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_env.py

# Start server
python -m uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

# In another terminal, test API
curl -X POST http://localhost:8000/reset -H "Content-Type: application/json" -d '{"task_type": "easy"}'
```

### Docker Deployment

```bash
# Build image
docker build -t cloud-infra-optimizer:latest .

# Run container
docker run -p 8000:8000 cloud-infra-optimizer:latest
```

### Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Choose "Docker" runtime
3. Connect your GitHub repository
4. The space will automatically deploy using `Dockerfile` and `openenv.yaml`

### Baseline Inference

```bash
export OPENAI_API_KEY="your-api-key"
python baseline_inference.py --task all
```

## Hackathon Compliance Checklist

- ✅ **Real-world task simulation**: Cloud infrastructure management (not games or toys)
- ✅ **Full OpenEnv spec**: Typed models, step/reset/state API, openenv.yaml
- ✅ **3 tasks with graders**: Easy (scale), Medium (optimize), Hard (recover)
- ✅ **Meaningful rewards**: Partial progress signals, penalties, completion bonuses
- ✅ **Baseline script**: Uses Claude API, reproducible scores
- ✅ **Docker + Dockerfile**: Ready for Hugging Face Spaces
- ✅ **Comprehensive README**: Setup, API docs, examples

## Evaluation Criteria

The environment is designed to be evaluated on:

1. **Realism**: Cloud infrastructure management is a genuine use case
2. **Complexity**: Three tasks with increasing difficulty levels
3. **Reward Design**: Meaningful signals guide agent learning
4. **Reproducibility**: Deterministic environment, baseline script
5. **Deployment**: Docker-ready for immediate deployment
6. **Documentation**: Complete guides for setup, API, and deployment

## Innovation Highlights

- **Progressive Difficulty**: Tasks increase in complexity, allowing agents to learn incrementally
- **Multi-Objective Optimization**: Balance performance, cost, and reliability
- **Realistic Metrics**: Uptime, response time, error rate, monthly cost
- **Flexible Actions**: Multiple ways to achieve objectives, encouraging creative solutions
- **Extensible Design**: Easy to add new tasks, actions, or infrastructure components

## Future Extensions

The environment can be extended with:

- Additional infrastructure components (CDN, caching, monitoring)
- More complex failure scenarios (cascading failures, network partitions)
- Time-series data (traffic patterns, seasonal variations)
- Multi-agent scenarios (competing teams managing shared resources)
- Integration with real cloud APIs (AWS, GCP, Azure)

## Support & Documentation

- **README.md**: Complete API documentation and usage examples
- **DEPLOYMENT.md**: Step-by-step deployment guide
- **test_env.py**: Validation script with examples
- **baseline_inference.py**: Reference implementation using Claude API
- **Code Comments**: Detailed comments explaining environment logic

## Contact & Attribution

**Created for**: Open Env Hackathon Bangalore 2026
**Environment**: Cloud Infrastructure Optimizer
**Specification**: OpenEnv v1.0
**Framework**: FastAPI + Pydantic + Docker

---

## Getting Started

1. **Review the README.md** for complete API documentation
2. **Run test_env.py** to verify the environment works
3. **Start the server** locally or in Docker
4. **Run baseline_inference.py** to see the agent in action
5. **Deploy to Hugging Face Spaces** for public access

Good luck with the hackathon! 🚀
