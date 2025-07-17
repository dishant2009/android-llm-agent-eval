"""Utility helpers for android-llm-agent-eval."""
from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, List

from fuzzywuzzy import fuzz, process

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VALID_ACTIONS_WITH_PARAM: List[str] = [
    "CLICK",
    "TYPE",
    "LONG_CLICK",
]

VALID_ACTIONS_NO_PARAM: List[str] = [
    "SCROLL_UP",
    "SCROLL_DOWN",
    "PRESS_BACK",
    "PRESS_HOME",
    "SWIPE_LEFT",
    "SWIPE_RIGHT",
]

# ---------------------------------------------------------------------------
# Dataset helpers
# ---------------------------------------------------------------------------

def load_android_world_data(data_path: str) -> List[Dict]:
    """Load and parse AndroidWorld episode JSON files."""
    data_dir = Path(data_path)
    if not data_dir.exists():
        raise FileNotFoundError(
            f"AndroidWorld data directory not found at {data_dir}. "
            "Run `scripts/setup.sh` or set ANDROID_WORLD_DATA env var."
        )

    episodes: List[Dict] = []
    for file in data_dir.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as fp:
                episodes.append(json.load(fp))
        except json.JSONDecodeError as exc:  # pragma: no cover
            logger.warning("Failed to parse %s – %s", file, exc)
    episodes.sort(key=lambda e: e.get("episode_id"))
    return episodes

# ---------------------------------------------------------------------------
# Action helpers
# ---------------------------------------------------------------------------

def _extract_param(action: str) -> str:
    try:
        return action.split("(", 1)[1].rstrip(")").strip("\"'")
    except Exception:  # noqa: BLE001
        return ""

def validate_action(action: str, ui_elements: List[str]) -> bool:
    action = action.strip()

    if any(action.startswith(f"{name}(") for name in VALID_ACTIONS_WITH_PARAM):
        # Expect a parameter inside parentheses
        element_name = _extract_param(action)
        return element_name in ui_elements

    if any(action == f"{name}()" for name in VALID_ACTIONS_NO_PARAM):
        return True

    return False

def compare_actions(predicted: str, ground_truth: str) -> Dict:
    """Return dict with exact match bool & fuzzy ratio (0-100)."""
    exact_match = predicted.strip() == ground_truth.strip()
    fuzzy_score = fuzz.ratio(predicted.strip(), ground_truth.strip())
    return {
        "exact_match": exact_match,
        "fuzzy_score": fuzzy_score,
    }

# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------

def setup_android_world(target_dir: str = "./android_world") -> None:  # pragma: no cover
    """Clone `android_world` dataset repo if not already present."""
    target_path = Path(target_dir)
    if target_path.exists():
        logger.info("android_world repo already present at %s", target_path)
        return

    logger.info("Cloning android_world repository to %s", target_path)
    try:
        subprocess.check_call(
            ["git", "clone", "https://github.com/google-research/android_world.git", target_dir]
        )
    except subprocess.CalledProcessError as exc:
        logger.error("Failed to clone android_world: %s", exc)
        raise RuntimeError("Failed to clone android_world repository") from exc 