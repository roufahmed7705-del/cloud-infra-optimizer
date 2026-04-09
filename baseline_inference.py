#!/usr/bin/env python3
"""
Baseline Inference Script for Cloud Infrastructure Optimizer

Uses OpenAI API to run an agent against the environment and produce
reproducible scores on all 3 tasks.

Usage:
    python baseline_inference.py --api-key YOUR_API_KEY --task easy
"""

import argparse
import json
import os
import sys
from typing import Optional
import requests
from openai import OpenAI

# Environment configuration
ENV_URL = os.getenv("ENV_URL", "http://localhost:8000")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def create_client(api_key: str) -> OpenAI:
    """Create OpenAI client."""
    return OpenAI(api_key=api_key)


def reset_environment(task_type: str) -> dict:
    """Reset the environment for a specific task."""
    response = requests.post(
        f"{ENV_URL}/reset",
        json={"task_type": task_type},
    )
    response.raise_for_status()
    return response.json()


def step_environment(action: dict) -> dict:
    """Execute one step in the environment."""
    response = requests.post(
        f"{ENV_URL}/step",
        json=action,
    )
    response.raise_for_status()
    return response.json()


def get_state() -> dict:
    """Get current environment state."""
    response = requests.get(f"{ENV_URL}/state")
    response.raise_for_status()
    return response.json()


def run_inference(task_type: str, client: OpenAI, max_steps: int = 50) -> dict:
    """Run inference on a specific task."""
    print(f"\n{'='*60}")
    print(f"Running inference on task: {task_type}")
    print(f"{'='*60}\n")

    # Reset environment
    observation = reset_environment(task_type)
    print(f"Task: {observation['info']['task_type']}")
    print(f"Description: {observation['message']}\n")

    total_reward = 0.0
    episode_data = {
        "task": task_type,
        "steps": [],
        "total_reward": 0.0,
        "final_progress": 0.0,
        "success": False,
    }

    for step_num in range(max_steps):
        # Get current state
        state = get_state()
        infra = state["infrastructure_state"]

        # Build context for the agent
        context = f"""
Current Infrastructure State:
- Web Servers: {infra['web_servers']['count']} x {infra['web_servers']['instance_type']} (${infra['web_servers']['hourly_cost']}/hr each)
- App Servers: {infra['app_servers']['count']} x {infra['app_servers']['instance_type']} (${infra['app_servers']['hourly_cost']}/hr each)
- Database: {infra['database']['engine']} {infra['database']['instance_size']} with {infra['database']['replicas']} replicas (${infra['database']['hourly_cost']}/hr)
- Load Balancer: {'Active' if infra['load_balancer_active'] else 'DOWN'}
- Monthly Cost: ${infra['total_monthly_cost']:.2f}
- Uptime: {infra['uptime_percentage']:.1f}%
- Response Time: {infra['response_time_ms']:.0f}ms
- Error Rate: {infra['error_rate']*100:.1f}%

Task: {state['task_description']}
Progress: {observation['task_progress']*100:.1f}%
Step: {step_num + 1}/{max_steps}

Available actions:
1. scale_up: Increase instance count (web_servers, app_servers)
2. scale_down: Decrease instance count
3. change_instance: Change instance type (web_servers, app_servers, database)
4. add_replica: Add database replicas
5. remove_replica: Remove database replicas
6. failover: Restore failed load balancer

Respond with a JSON action in this format:
{{"action_type": "...", "target": "...", "value": ..., "instance_type": "..."}}
"""

        # Call OpenAI API
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[
                    {
                        "role": "user",
                        "content": context,
                    }
                ],
            )
            response_text = response.content[0].text
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            print("Using random action instead...")
            action = {
                "action_type": "scale_up",
                "target": "web_servers",
                "value": 5,
            }
            response_text = json.dumps(action)

        # Parse action
        try:
            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                action_json = response_text[json_start:json_end]
                action = json.loads(action_json)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"Error parsing action: {e}")
            print(f"Response: {response_text}")
            continue

        # Execute action
        try:
            observation = step_environment(action)
            reward = observation["reward"]
            done = observation["done"]
            task_progress = observation["task_progress"]

            total_reward += reward
            episode_data["steps"].append(
                {
                    "step": step_num + 1,
                    "action": action,
                    "reward": reward,
                    "progress": task_progress,
                    "message": observation["message"],
                }
            )

            print(f"Step {step_num + 1}: {observation['message']}")
            print(f"  Reward: {reward:.2f}, Progress: {task_progress*100:.1f}%\n")

            if done:
                print(f"Episode finished at step {step_num + 1}")
                episode_data["success"] = task_progress >= 0.95
                break

        except Exception as e:
            print(f"Error executing action: {e}")
            continue

    episode_data["total_reward"] = total_reward
    episode_data["final_progress"] = observation["task_progress"]
    episode_data["success"] = observation["task_progress"] >= 0.95

    return episode_data


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Baseline inference for Cloud Infrastructure Optimizer"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=OPENAI_API_KEY,
        help="OpenAI API key",
    )
    parser.add_argument(
        "--task",
        type=str,
        choices=["easy", "medium", "hard", "all"],
        default="all",
        help="Task to run",
    )
    parser.add_argument(
        "--env-url",
        type=str,
        default=ENV_URL,
        help="Environment URL",
    )

    args = parser.parse_args()

    if not args.api_key:
        print("Error: OPENAI_API_KEY not set. Use --api-key or set OPENAI_API_KEY env var")
        sys.exit(1)

    client = create_client(args.api_key)

    tasks = ["easy", "medium", "hard"] if args.task == "all" else [args.task]
    results = {}

    for task in tasks:
        try:
            result = run_inference(task, client)
            results[task] = result
        except Exception as e:
            print(f"Error running inference on {task}: {e}")
            results[task] = {"error": str(e)}

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")

    for task, result in results.items():
        if "error" in result:
            print(f"{task.upper()}: ERROR - {result['error']}")
        else:
            print(f"{task.upper()}:")
            print(f"  Total Reward: {result['total_reward']:.2f}")
            print(f"  Final Progress: {result['final_progress']*100:.1f}%")
            print(f"  Success: {'✓' if result['success'] else '✗'}")
            print(f"  Steps: {len(result['steps'])}")
            print()

    # Save results
    with open("baseline_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to baseline_results.json")


if __name__ == "__main__":
    main()
