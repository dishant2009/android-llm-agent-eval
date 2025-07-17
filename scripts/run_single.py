#!/usr/bin/env python3
"""Run a single AndroidWorld episode using specified model/strategy."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from src.agent import AndroidAgent
from src.llm_client import LLMClient
from src.utils import load_android_world_data


def parse_args():
    parser = argparse.ArgumentParser(description="Run a single episode")
    parser.add_argument("--episode", required=True, help="Episode ID (e.g. install_app_001)")
    parser.add_argument("--provider", default=os.getenv("DEFAULT_LLM_PROVIDER", "openai"))
    parser.add_argument("--model", default=os.getenv("DEFAULT_MODEL", "gpt-4-turbo"))
    parser.add_argument("--strategy", default="base", choices=["base", "few_shot", "reflection"])
    parser.add_argument("--data_path", default=os.getenv("ANDROID_WORLD_DATA", "./android_world/data"))
    return parser.parse_args()


def main():
    args = parse_args()
    episodes = load_android_world_data(args.data_path)
    episode = next((e for e in episodes if e["episode_id"] == args.episode), None)
    if episode is None:
        raise SystemExit(f"Episode '{args.episode}' not found in {args.data_path}")

    llm = LLMClient(provider=args.provider, model=args.model)
    agent = AndroidAgent(llm, prompt_strategy=args.strategy)

    print(f"Goal: {episode['goal']}")
    for step in episode["steps"]:
        action = agent.step(episode["goal"], step["observation"])
        print(f"Observation App={step['observation']['app_name']} | Action: {action}")


if __name__ == "__main__":
    main() 