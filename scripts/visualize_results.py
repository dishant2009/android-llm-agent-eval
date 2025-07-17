#!/usr/bin/env python3
"""Visualize evaluation episode progress.

Usage (CLI):
  python scripts/visualize_results.py --episode calculator_sum_001
  python scripts/visualize_results.py          # interactive chooser (requires rich)

Usage (Streamlit):
  python scripts/visualize_results.py --web    # launches Streamlit inside the script
  streamlit run scripts/visualize_results.py   # native Streamlit entrypoint

The tool reads JSON files produced by the evaluation pipeline in the *results/*
folder and displays per-step information such as predicted vs. ground-truth
actions and exact-match status.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import List, Dict

# ---------------------------------------------------------------------------
# Optional dependencies
# ---------------------------------------------------------------------------
try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt

    RICH_AVAILABLE = True
except ImportError:  # pragma: no cover
    RICH_AVAILABLE = False

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RESULTS_DIR = Path("results")


def _load_episode(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as fp:
        return json.load(fp)


def _list_episode_files() -> List[Path]:
    return sorted(RESULTS_DIR.glob("episode_*.json"))

# ---------------------------------------------------------------------------
# CLI rendering with Rich
# ---------------------------------------------------------------------------

def _render_cli(episode_data: Dict) -> None:  # pragma: no cover – UI function
    if not RICH_AVAILABLE:
        print(json.dumps(episode_data, indent=2))
        return

    console = Console()
    title = f"Episode {episode_data['episode_id']} – {'✅' if episode_data['success'] else '❌'}"
    table = Table(title=title)
    table.add_column("Step", justify="right")
    table.add_column("App")
    table.add_column("Predicted", style="yellow")
    table.add_column("Ground Truth", style="cyan")
    table.add_column("Match", justify="center")

    for idx, step in enumerate(episode_data["steps"]):
        match = "✅" if step["exact_match"] else "❌"
        table.add_row(
            str(idx),
            step["observation"]["app_name"],
            step["predicted"],
            step["ground_truth"],
            match,
        )

    console.print(table)

# ---------------------------------------------------------------------------
# Streamlit rendering
# ---------------------------------------------------------------------------

def _render_streamlit(all_episodes: List[Dict]) -> None:  # pragma: no cover – UI function
    import streamlit as st  # Local import so base CLI users aren't forced to install

    st.set_page_config(page_title="AndroidWorld Episode Viewer", layout="wide")
    st.sidebar.title("Episode Viewer")

    episode_ids = [ep["episode_id"] for ep in all_episodes]
    selected_id = st.sidebar.selectbox("Choose episode", episode_ids)
    episode = next(ep for ep in all_episodes if ep["episode_id"] == selected_id)

    st.header(f"Episode {episode['episode_id']}")
    st.markdown(f"**Success**: {'✅' if episode['success'] else '❌'}")

    # Build a DataFrame-friendly structure
    rows = []
    for idx, step in enumerate(episode["steps"]):
        rows.append(
            {
                "step": idx,
                "app": step["observation"]["app_name"],
                "predicted": step["predicted"],
                "ground_truth": step["ground_truth"],
                "match": "✅" if step["exact_match"] else "❌",
            }
        )

    st.dataframe(rows, use_container_width=True)

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(description="Visualize episode evaluation results")
    parser.add_argument(
        "--episode",
        help="Episode ID to visualise (omit for interactive chooser)",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch Streamlit web UI instead of CLI table.",
    )
    args, unknown = parser.parse_known_args()

    # -------------------------------------------------------------------
    # WEB UI: re-invoke script through the Streamlit CLI to obtain proper
    # runtime context (avoids "missing ScriptRunContext" warning).
    # -------------------------------------------------------------------
    if args.web:
        import subprocess
        import sys

        # Ensure Streamlit is installed before spawning new process
        try:
            import streamlit  # type: ignore  # noqa: F401
        except ImportError as exc:  # pragma: no cover
            print(
                "Streamlit not installed – install with `pip install streamlit` "
                "or run without --web."
            )
            raise SystemExit(1) from exc

        # Build command: streamlit run <script> -- <original args minus --web>
        script_path = Path(__file__).resolve()
        remaining = [a for a in sys.argv[1:] if a != "--web"]
        cmd = [sys.executable, "-m", "streamlit", "run", str(script_path), "--"] + remaining

        # Replace current process (so ^C propagates correctly)
        os.execvp(cmd[0], cmd)

    # -------------------------------------------------------------------
    # If the script is already running inside a Streamlit context (e.g. when
    # invoked via `streamlit run`), render the web UI immediately.
    # -------------------------------------------------------------------
    in_streamlit = False
    try:
        import streamlit as st  # type: ignore

        # Newer Streamlit versions provide runtime.exists(); older ones expose
        # a private flag. We check both for maximum compatibility.
        try:
            in_streamlit = st.runtime.exists()
        except Exception:  # pragma: no cover – attribute may not exist
            in_streamlit = getattr(st, "_is_running_with_streamlit", False)
    except ImportError:
        pass

    if in_streamlit:
        episodes = [_load_episode(p) for p in _list_episode_files()]
        _render_streamlit(episodes)
        return

    # --------------- CLI mode ----------------
    episode_files = _list_episode_files()
    if not episode_files:
        print("No episode result files found. Run evaluation first.")
        return

    if args.episode:
        target_path = RESULTS_DIR / f"episode_{args.episode}.json"
        if not target_path.exists():
            print(f"Episode file {target_path.name} not found in {RESULTS_DIR}")
            return
    else:
        if RICH_AVAILABLE:
            console = Console()
            console.print("[bold]Select episode to view[/bold]")
            mapping = {str(i): p for i, p in enumerate(episode_files)}
            for idx, p in mapping.items():
                console.print(f"[{idx}] {p.name}")
            choice = Prompt.ask("Choice", default="0")
            target_path = mapping.get(choice, episode_files[0])
        else:
            target_path = episode_files[0]
            print(
                f"rich not installed – defaulting to {target_path.name}. Install with `pip install rich` for interactive selection."
            )

    data = _load_episode(target_path)
    _render_cli(data)


if __name__ == "__main__":
    main() 