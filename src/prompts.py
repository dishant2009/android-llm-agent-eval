"""Prompt templates and rendering helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "prompts"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)

# ---------------------------------------------------------------------------
# Template helpers
# ---------------------------------------------------------------------------

def _get_template(name: str):
    return _env.get_template(name)


def base_prompt(goal: str, observation: Dict[str, Any], history: List[Dict[str, Any]]):
    tpl = _get_template("base_template.md")
    return tpl.render(goal=goal, observation=observation, history=history)


def reflection_prompt(goal: str, observation: Dict[str, Any], history: List[Dict[str, Any]]):
    tpl = _get_template("reflection_template.md")
    return tpl.render(goal=goal, observation=observation, history=history)


def few_shot_prompt(goal: str, observation: Dict[str, Any], history: List[Dict[str, Any]]):
    examples_file = TEMPLATE_DIR / "few_shot_examples.json"
    tpl = _get_template("base_template.md")

    with open(examples_file, "r", encoding="utf-8") as fp:
        examples = json.load(fp)[:5]

    rendered_examples: List[str] = []
    for ex in examples:
        rendered_examples.append(
            f"Goal: {ex['goal']}\n"
            f"Observation: {ex['observation']}\n"
            f"Reasoning: {ex['reasoning']}\n"
            f"Action: {ex['action']}\n"
        )

    header = "\n".join(rendered_examples) + "\n---\n"
    return header + tpl.render(goal=goal, observation=observation, history=history) 