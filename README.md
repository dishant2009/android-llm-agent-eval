# Android LLM Agent Evaluation Framework

A comprehensive evaluation framework for testing Large Language Model (LLM) agents in mobile environments. This repository implements the **QualGent Research Coding Challenge** and benchmarks how well LLM agents (GPT-4, Claude-3) can navigate Android applications by interpreting UI observations and generating valid actions.

**Repository**: [https://github.com/dishant2009/android-llm-agent-eval](https://github.com/dishant2009/android-llm-agent-eval)

## Key Features

- **Multi-Provider Support**: Unified interface for OpenAI GPT-4 and Anthropic Claude-3
- **Advanced Prompting Strategies**: Base, few-shot, and self-reflection prompting approaches
- **Comprehensive Evaluation Metrics**: Step accuracy, episode success rates, and failure analysis
- **Memory Buffer Integration**: Context-aware action selection with configurable history tracking
- **Interactive Visualization**: Real-time Streamlit dashboard for monitoring and analysis
- **Production-Ready Architecture**: Robust error handling, retry mechanisms, and comprehensive logging
- **Extensible Design**: Modular structure for easy addition of new models and strategies

## Performance Highlights

| Provider  | Strategy   | Success Rate | Step Accuracy |
|-----------|------------|--------------|---------------|
| OpenAI    | Few-shot   | 40.0%        | 77.1%         |
| Anthropic | Few-shot   | 60.0%        | 88.6%         |
| OpenAI    | Base       | 20.0%        | 62.9%         |

## Quick Start

### Prerequisites
- Python 3.11 or higher
- OpenAI API key (for GPT-4 access)
- Anthropic API key (for Claude-3 access)

### Installation

```bash
# Clone the repository
git clone https://github.com/dishant2009/android-llm-agent-eval.git
cd android-llm-agent-eval

# Set up virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies and download dataset
bash scripts/setup.sh

# Configure API keys
cp dot_env_example .env
# Edit .env file with your API keys
```

### Basic Usage

```bash
# Run evaluation on 10 episodes with GPT-4 using few-shot prompting
python scripts/run_evaluation.py --episodes 10 --models openai --strategies few_shot

# Test single episode with detailed output
python scripts/run_single.py --episode install_app_001 --provider openai --strategy few_shot

# Launch interactive visualization dashboard
python -m streamlit run scripts/visualize_results.py
```

## Repository Structure

```
android-llm-agent-eval/
├── src/                    # Core framework implementation
│   ├── agent.py           # LLM agent with memory buffer integration
│   ├── llm_client.py      # Unified LLM provider interface
│   ├── prompts.py         # Jinja2 templating system
│   ├── evaluate.py        # Comprehensive evaluation engine
│   └── utils.py           # Dataset loading and validation utilities
├── prompts/               # Prompt templates and examples
│   ├── base_template.md   # Simple goal-to-action prompting
│   ├── few_shot_examples.json  # Curated training examples
│   └── reflection_template.md  # Self-reflection prompting
├── scripts/               # Command-line utilities
│   ├── setup.sh          # Environment setup automation
│   ├── run_single.py     # Single episode testing
│   ├── run_evaluation.py # Batch evaluation across strategies
│   └── visualize_results.py  # Streamlit dashboard
├── results/               # Auto-generated evaluation results
├── tests/                 # Comprehensive test suite
├── android_world/         # Dataset (auto-downloaded)
├── config.yaml           # Experiment configuration
├── requirements.txt       # Python dependencies
└── report.md             # Detailed research findings
```

## Configuration

### Environment Variables (.env)

```bash
# Required API keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional configuration
ANDROID_WORLD_DATA=./android_world/data
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo
```

### Experiment Configuration (config.yaml)

```yaml
evaluation:
  num_episodes: 15
  max_steps_per_episode: 20
  timeout_seconds: 30

models:
  openai:
    model: "gpt-4-turbo"
    temperature: 0.1
    max_tokens: 150
  anthropic:
    model: "claude-3-sonnet-20240229"
    temperature: 0.1
    max_tokens: 150

prompting:
  max_history_steps: 5
  include_reasoning: true
  retry_on_invalid: true
  max_retries: 3
```

## Advanced Usage

### Comprehensive Model Comparison

```bash
# Compare all strategies across multiple providers
python scripts/run_evaluation.py \
  --episodes 10 \
  --models openai,anthropic \
  --strategies base,few_shot,reflection
```

### Custom Episode Testing

```bash
# Test specific episodes with detailed logging
python scripts/run_single.py \
  --episode audio_recorder_001 \
  --provider anthropic \
  --strategy few_shot
```

### Interactive Visualization and Analysis

```bash
# Launch comprehensive results dashboard
python -m streamlit run scripts/visualize_results.py
```

The Streamlit dashboard provides:
- Real-time evaluation monitoring
- Interactive performance metrics visualization
- Detailed failure pattern analysis
- Provider comparison charts
- Episode-level drill-down capabilities
- Configuration management interface

## Evaluation Metrics

### Primary Metrics
- **Step Accuracy**: Percentage of individual actions matching ground truth
- **Episode Success Rate**: Percentage of complete task sequences executed correctly
- **Fuzzy Match Scores**: Semantic similarity analysis for near-miss evaluation

### Advanced Analysis
- Action type distribution and error patterns
- Hallucination detection and frequency analysis
- UI reasoning capability assessment
- Memory buffer effectiveness measurement

## Output Files

The evaluation system generates structured results:

```bash
results/
├── episode_<id>.json          # Detailed per-episode logs
├── summary_<timestamp>.json   # Aggregated performance metrics
├── comparison_<timestamp>.json # Cross-model comparison data
└── detailed_failure_analysis.json # Systematic failure patterns
```

### Example Output Structure

```json
{
  "episode_id": "install_app_001",
  "goal": "Install the Twitter app from the Play Store",
  "success": false,
  "steps": [
    {
      "observation": {
        "app_name": "Home Screen",
        "ui_elements": ["Play Store", "Settings", "Chrome"],
        "screen_text": "Welcome to Android"
      },
      "predicted": "CLICK(\"Play Store\")",
      "ground_truth": "CLICK(\"Play Store\")",
      "exact_match": true,
      "fuzzy_score": 100
    }
  ]
}
```

## Testing and Quality Assurance

### Running Tests

```bash
# Execute full test suite
pytest tests/ -v

# Run specific test categories
pytest tests/test_agent.py -v      # Agent functionality
pytest tests/test_utils.py -v      # Utility functions
pytest tests/test_evaluate.py -v   # Evaluation metrics
```

### Code Quality Checks

```bash
# Linting and formatting (if configured)
flake8 src/
black src/
```

## Research Findings

### Key Insights

1. **Few-shot prompting significantly outperforms base prompting** across all providers
2. **Claude demonstrates superior performance** when format issues are resolved (89% vs 77% step accuracy)
3. **Quote formatting inconsistencies** represent a critical deployment challenge
4. **Memory buffer integration** improves multi-step task performance
5. **Action type confusion** (TYPE vs CLICK) is a primary failure mode

### Systematic Failure Patterns

- **Hallucinated Actions** (15% of failures): References to non-existent UI elements
- **Goal Misinterpretation** (25% of first-step failures): Incorrect initial navigation
- **Action Type Confusion** (40% of mid-sequence failures): TYPE vs CLICK distinction
- **Format Incompatibility** (Critical): Quote style variations cause validation failures

## Contributing

### Development Setup

```bash
# Clone and set up development environment
git clone https://github.com/dishant2009/android-llm-agent-eval.git
cd android-llm-agent-eval
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Adding New Providers

1. Extend `src/llm_client.py` with new provider integration
2. Add provider-specific configuration to `config.yaml`
3. Update evaluation scripts to include new provider
4. Add comprehensive tests for new functionality

### Adding New Prompting Strategies

1. Create new template in `prompts/` directory
2. Register strategy in `src/prompts.py`
3. Update evaluation framework to support new strategy
4. Document strategy rationale and expected performance

## Troubleshooting

### Common Issues

**Import Errors**: Ensure virtual environment is activated and PYTHONPATH is set:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**API Rate Limiting**: The framework includes automatic retry mechanisms with exponential backoff

**Missing Dataset**: Run setup script to download android_world data:
```bash
bash scripts/setup.sh
```

**Quote Format Issues**: Update validation logic to handle both single and double quotes

## Citation

If you use this framework in your research, please cite:

```bibtex
@misc{android-llm-agent-eval,
  author = {Dishant Digdarshi},
  title = {Android LLM Agent Evaluation Framework},
  year = {2025},
  url = {https://github.com/dishant2009/android-llm-agent-eval}
}
```

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- QualGent Research for the original coding challenge
- Google Research for the AndroidWorld environment
- OpenAI and Anthropic for LLM API access

---

For detailed research findings, methodology, and performance analysis, see [report.md](report.md).
