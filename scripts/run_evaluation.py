#!/usr/bin/env python3
"""Run full evaluation comparing prompting strategies and models.

Usage: python scripts/run_evaluation.py --episodes 15 --models openai,anthropic
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from src.agent import AndroidAgent
from src.evaluate import evaluate_episodes
from src.llm_client import LLMClient
from src.utils import load_android_world_data


def parse_args():
    parser = argparse.ArgumentParser(description="Run batch evaluation on AndroidWorld episodes")
    parser.add_argument("--episodes", type=int, default=15, help="Number of episodes to evaluate")
    parser.add_argument("--models", default="openai", help="Comma-separated providers (openai,anthropic)")
    parser.add_argument(
        "--strategies",
        default="base,few_shot,reflection",
        help="Comma-separated prompt strategies",
    )
    parser.add_argument("--data_path", default=os.getenv("ANDROID_WORLD_DATA", "./android_world/data"))
    return parser.parse_args()


def main():
    args = parse_args()
    episodes = load_android_world_data(args.data_path)[: args.episodes]

    comparison: list[dict] = []
    for provider in [p.strip() for p in args.models.split(",") if p.strip()]:
        for strategy in [s.strip() for s in args.strategies.split(",") if s.strip()]:
            print(f"\n=== Evaluating provider={provider} | strategy={strategy} ===")
            llm = LLMClient(provider=provider)
            agent = AndroidAgent(llm, prompt_strategy=strategy)
            metrics = evaluate_episodes(agent, episodes, num_episodes=len(episodes))
            comparison.append({"provider": provider, "strategy": strategy, **metrics})

    # Save comparison file
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True, parents=True)
    out_file = results_dir / f"comparison_{datetime.utcnow().isoformat()}.json"
    with open(out_file, "w", encoding="utf-8") as fp:
        json.dump(comparison, fp, indent=2)

    # Print summary table
    print("\nProvider | Strategy | Success Rate | Step Accuracy")
    for entry in comparison:
        print(
            f"{entry['provider']} | {entry['strategy']} | "
            f"{entry['success_rate']*100:.1f}% | {entry['step_accuracy']*100:.1f}%"
        )
    print(f"\nDetailed results saved to {out_file}\n")


if __name__ == "__main__":
    main() 