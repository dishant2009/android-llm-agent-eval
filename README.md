# Android LLM Agent Evaluation Framework

This repository implements the **QualGent Research Coding Challenge – Evaluating LLM Agents in Android World**. It benchmarks how well large-language-model (LLM) agents (GPT-4, Claude-3) can navigate Android apps by interpreting UI observations and returning valid actions.

## 🔧 Quick Start (3 commands)
```bash
# 1️⃣  Clone repo & enter directory
$ git clone <url> android-llm-agent-eval && cd android-llm-agent-eval

# 2️⃣  Install deps & download dataset
$ bash scripts/setup.sh

# 3️⃣  Run evaluation (15 episodes, GPT-4 w/ base prompt)
$ python scripts/run_evaluation.py --episodes 15 --models openai --strategies base
```

> **Note**: Copy `dot_env_example` to `.env` and add your API keys before running.

## 📂 Repository Layout
```
src/            Core library (agent, prompts, evaluation, utils, llm client)
prompts/        Jinja2 templates + few-shot examples
scripts/        CLI utilities for setup, single-run, batch evaluation
results/        Auto-generated logs & metrics
tests/          Pytest unit & integration tests
config.yaml     Default experiment configuration
requirements.txt Python dependencies
```

## 🏃 Usage Examples

### Single Episode
```bash
python scripts/run_single.py --episode install_app_001 --provider openai --strategy few_shot
```

### Batch Evaluation Across Models
```bash
python scripts/run_evaluation.py --episodes 15 --models openai,anthropic --strategies base,few_shot,reflection
```

## ⚙️ Environment Variables (`.env`)
| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI GPT-4 access |
| `ANTHROPIC_API_KEY` | Claude-3 access |
| `ANDROID_WORLD_DATA` | Path to episode JSONs (auto-downloaded) |
| `DEFAULT_LLM_PROVIDER` | openai / anthropic |
| `DEFAULT_MODEL` | e.g. gpt-4-turbo |

## 📊 Output Format
The evaluation script creates:
* `results/episode_<id>.json` – per-step predictions & match scores.
* `results/summary_<timestamp>.json` – aggregated metrics.
* `results/comparison_<timestamp>.json` – cross-model summary.

## 🧪 Testing
Run the unit test suite with **pytest**:
```bash
pytest -q
```

## 📄 License
MIT 