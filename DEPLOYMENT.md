# Deployment Guide

## Local Development

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd cloud_infra_env
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server**:
   ```bash
   python -m uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Test the environment**:
   ```bash
   # In another terminal
   curl -X POST http://localhost:8000/reset \
     -H "Content-Type: application/json" \
     -d '{"task_type": "easy"}'
   ```

## Docker Deployment

### Build the Image

```bash
docker build -t cloud-infra-optimizer:latest .
```

### Run Locally

```bash
docker run -p 8000:8000 cloud-infra-optimizer:latest
```

The server will be available at `http://localhost:8000`

### Push to Docker Registry

```bash
# Tag the image
docker tag cloud-infra-optimizer:latest your-registry/cloud-infra-optimizer:latest

# Push to registry
docker push your-registry/cloud-infra-optimizer:latest
```

## Hugging Face Spaces Deployment

### Prerequisites
- Hugging Face account
- GitHub repository with the code

### Steps

1. **Create a new Space on Hugging Face**:
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Choose a name (e.g., `cloud-infra-optimizer`)
   - Select "Docker" as the runtime
   - Create the space

2. **Connect your GitHub repository**:
   - In the Space settings, connect your GitHub repo
   - Select the branch to deploy from

3. **Configure the Space**:
   - The space will automatically detect `openenv.yaml` and `Dockerfile`
   - The deployment will use these files to build and run the environment

4. **Access the environment**:
   - The space will provide a public URL
   - API endpoints will be available at `https://your-username-space-name.hf.space/`

### Example API Calls

```bash
# Reset environment
curl -X POST https://your-username-space-name.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_type": "easy"}'

# Execute action
curl -X POST https://your-username-space-name.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "scale_up",
    "target": "web_servers",
    "value": 5
  }'

# Get state
curl https://your-username-space-name.hf.space/state
```

## Baseline Inference

### Setup

1. **Set your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

2. **Run the baseline agent**:
   ```bash
   # Test a single task
   python baseline_inference.py --task easy

   # Run all tasks
   python baseline_inference.py --task all

   # Against a remote environment
   python baseline_inference.py --task easy --env-url https://your-space.hf.space
   ```

3. **Results**:
   - Results are saved to `baseline_results.json`
   - Contains total reward, progress, and step-by-step actions

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Docker Build Fails
- Ensure all files are in the correct locations
- Check Docker is installed: `docker --version`
- Try building with verbose output: `docker build -t cloud-infra-optimizer:latest . --progress=plain`

### API Connection Issues
- Verify server is running: `curl http://localhost:8000/health`
- Check firewall settings
- Ensure correct URL format in requests

### Import Errors
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)
- Ensure you're in the correct directory

## Performance Optimization

### For Production Deployment

1. **Use a production ASGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker server.app:app
   ```

2. **Enable CORS** (if needed):
   - Update `server/app.py` to add CORS middleware
   - Configure allowed origins

3. **Add monitoring**:
   - Use Prometheus for metrics
   - Set up logging aggregation
   - Monitor response times and error rates

4. **Scale horizontally**:
   - Deploy multiple instances behind a load balancer
   - Use container orchestration (Kubernetes, Docker Swarm)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 8000 |
| `HOST` | Server host | 0.0.0.0 |
| `OPENAI_API_KEY` | OpenAI API key for baseline | (required for inference) |
| `ENV_URL` | Environment URL for baseline | http://localhost:8000 |

## Testing

Run the included test script:

```bash
python test_env.py
```

This will:
- Test all three task types
- Verify action execution
- Confirm reward calculation
- Validate state transitions

## Support

For issues or questions:
1. Check the README.md for API documentation
2. Review the example code in `baseline_inference.py`
3. Check logs for error messages
4. Verify all dependencies are installed correctly
