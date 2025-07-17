"""LLM-powered agent that interacts with AndroidWorld episodes."""
from __future__ import annotations

import logging
from typing import Dict, List

from fuzzywuzzy import process

from .utils import (
    VALID_ACTIONS_WITH_PARAM,
    compare_actions,
    validate_action,
)
from .prompts import base_prompt, few_shot_prompt, reflection_prompt

logger = logging.getLogger(__name__)

PROMPT_RENDERERS = {
    "base": base_prompt,
    "few_shot": few_shot_prompt,
    "reflection": reflection_prompt,
}


class AndroidAgent:
    """Agent that selects actions based on UI observations."""

    def __init__(
        self,
        llm_client,
        prompt_strategy: str = "base",
        max_history: int = 5,
    ) -> None:
        if prompt_strategy not in PROMPT_RENDERERS:
            raise ValueError(
                f"Unknown prompt strategy '{prompt_strategy}'. Valid: {list(PROMPT_RENDERERS)}"
            )

        self.llm_client = llm_client
        self.prompt_strategy = prompt_strategy
        self.max_history = max_history
        self.history: List[Dict] = []  # List of {observation, action}

    # ------------------------------------------------------------------
    # Core loop
    # ------------------------------------------------------------------
    def step(self, goal: str, observation: Dict) -> str:
        """Compute next action for *observation* given *goal* and prior history."""
        prompt = self._build_prompt(goal, observation)
        raw_action = self.llm_client.generate_action(prompt)

        # ------------------------------------------------------------------
        # Extract the action line from the model response
        # ------------------------------------------------------------------
        import re

        ACTION_REGEX = re.compile(
            r"(CLICK\([^\n]+?\)|TYPE\([^\n]+?\)|LONG_CLICK\([^\n]+?\)|SCROLL_(UP|DOWN)\(\)|PRESS_(BACK|HOME)\(\)|SWIPE_(LEFT|RIGHT)\(\))"
        )

        action = ""
        lines = [ln.strip() for ln in raw_action.splitlines() if ln.strip()]

        # Scan lines for a valid action, even if preceded by 'Action:' or similar
        for ln in lines:
            # Direct validation first
            if validate_action(ln, observation.get("ui_elements", [])):
                action = ln
                break

            # Search within the line for an embedded action pattern
            match = ACTION_REGEX.search(ln)
            if match and validate_action(match.group(1), observation.get("ui_elements", [])):
                action = match.group(1)
                break

        # Fallbacks if nothing matched
        if not action and lines:
            # Attempt regex search across entire response
            match = ACTION_REGEX.search("\n".join(lines))
            if match:
                action = match.group(1)
            else:
                action = lines[0]

        # If still invalid, attempt automatic repair
        if not validate_action(action, observation.get("ui_elements", [])):
            logger.debug("Invalid action '%s' – attempting repair", action)
            action = self.repair_action(action, observation.get("ui_elements", []))

        # Track history for future context
        self.history.append({"observation": observation, "action": action})
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]
        return action

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_prompt(self, goal: str, observation: Dict) -> str:
        renderer = PROMPT_RENDERERS[self.prompt_strategy]
        recent_history = self.history[-self.max_history :]
        return renderer(goal=goal, observation=observation, history=recent_history)

    def repair_action(self, invalid_action: str, ui_elements: List[str]) -> str:
        """Attempt to "repair" invalid_action by fuzzy-matching UI elements."""
        for act in VALID_ACTIONS_WITH_PARAM:
            if invalid_action.startswith(act):
                # Extract param if provided
                try:
                    param = invalid_action.split("(", 1)[1].rstrip(")").strip("\"'")
                except Exception:  # noqa: BLE001
                    param = ""

                best_match, score = process.extractOne(param, ui_elements) if ui_elements else (None, 0)
                if best_match and score >= 60:
                    return f'{act}("{best_match}")'
                elif ui_elements:
                    return f'{act}("{ui_elements[0]}")'
        # Default safe action
        return "PRESS_BACK()" 