"""Evaluation utilities for AndroidWorld agent experiments."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from tqdm import tqdm

from .utils import compare_actions

logger = logging.getLogger(__name__)


def evaluate_episodes(
    agent,
    episodes: List[Dict],
    *,
    num_episodes: int = 10,
    results_dir: str | os.PathLike = "./results",
) -> Dict:
    """Run *agent* through *episodes* and compute aggregate metrics."""
    results_path = Path(results_dir)
    results_path.mkdir(exist_ok=True, parents=True)

    metrics: Dict[str, float | int | List] = {
        "total_episodes": 0,
        "successful_episodes": 0,
        "total_steps": 0,
        "correct_steps": 0,
        "episode_details": [],
    }

    for episode in tqdm(episodes[:num_episodes], desc="Evaluating"):
        episode_id = episode["episode_id"]
        goal = episode["goal"]
        steps = episode["steps"]

        ep_result = {
            "episode_id": episode_id,
            "steps": [],
            "success": False,
        }

        success = True
        for step in steps:
            obs = step["observation"]
            ground_truth = step["action"]
            predicted = agent.step(goal, obs)

            cmp = compare_actions(predicted, ground_truth)
            ep_result["steps"].append(
                {
                    "observation": obs,
                    "ground_truth": ground_truth,
                    "predicted": predicted,
                    **cmp,
                }
            )

            metrics["total_steps"] += 1
            if cmp["exact_match"]:
                metrics["correct_steps"] += 1
            else:
                success = False

        metrics["total_episodes"] += 1
        if success:
            metrics["successful_episodes"] += 1
            ep_result["success"] = True

        # Persist per-episode log
        with open(results_path / f"episode_{episode_id}.json", "w", encoding="utf-8") as fp:
            json.dump(ep_result, fp, indent=2)

        metrics["episode_details"].append(ep_result)

    # Aggregate scores
    metrics["step_accuracy"] = (
        metrics["correct_steps"] / metrics["total_steps"] if metrics["total_steps"] else 0.0
    )
    metrics["success_rate"] = (
        metrics["successful_episodes"] / metrics["total_episodes"] if metrics["total_episodes"] else 0.0
    )

    # Persist summary
    summary_file = results_path / f"summary_{datetime.utcnow().isoformat()}.json"
    with open(summary_file, "w", encoding="utf-8") as fp:
        json.dump(metrics, fp, indent=2)

    logger.info(
        "Finished evaluation – Success rate: %.2f%% | Step accuracy: %.2f%%",
        metrics["success_rate"] * 100,
        metrics["step_accuracy"] * 100,
    )
    return metrics 