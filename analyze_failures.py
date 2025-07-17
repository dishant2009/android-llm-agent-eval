"""Analyze LLM failures in detail for the benchmarking report."""

import json
import os
from pathlib import Path
from collections import defaultdict, Counter
import re


def analyze_action_type(action):
    """Categorize action types."""
    if action.startswith('CLICK('):
        return 'CLICK'
    elif action.startswith('TYPE('):
        return 'TYPE'
    elif action.startswith('SCROLL_'):
        return 'SCROLL'
    elif action.startswith('PRESS_'):
        return 'PRESS'
    elif action.startswith('SWIPE_'):
        return 'SWIPE'
    elif action.startswith('LONG_CLICK('):
        return 'LONG_CLICK'
    else:
        return 'UNKNOWN'


def extract_element_from_action(action):
    """Extract the UI element from CLICK/TYPE actions."""
    match = re.search(r'["\']([^"\']*)["\']', action)
    return match.group(1) if match else None


def is_hallucinated_action(predicted, ui_elements):
    """Check if action references non-existent UI elements."""
    if predicted.startswith('CLICK(') or predicted.startswith('LONG_CLICK('):
        element = extract_element_from_action(predicted)
        if element and element not in ui_elements:
            return True, element
    return False, None


def analyze_episode_results():
    """Analyze all episode results for failure patterns."""
    results_dir = Path("results")
    episode_files = list(results_dir.glob("episode_*.json"))

    if not episode_files:
        print(" No episode result files found. Run evaluation first!")
        return

    # Analysis containers
    failure_patterns = defaultdict(list)
    hallucinations = []
    action_type_errors = Counter()
    goal_misinterpretations = []
    ui_reasoning_failures = []

    total_steps = 0
    correct_steps = 0
    episodes_analyzed = 0

    print(" Analyzing episode results...")
    print("=" * 60)

    for episode_file in episode_files:
        try:
            with open(episode_file, 'r') as f:
                episode_data = json.load(f)

            episodes_analyzed += 1
            episode_id = episode_data.get('episode_id', 'unknown')
            steps = episode_data.get('steps', [])

            print(f"\n Episode: {episode_id}")
            print(f"   Success: {'✅' if episode_data.get('success', False) else '❌'}")

            for i, step in enumerate(steps):
                total_steps += 1
                predicted = step.get('predicted', '')
                ground_truth = step.get('ground_truth', '')
                observation = step.get('observation', {})
                ui_elements = observation.get('ui_elements', [])
                app_name = observation.get('app_name', 'Unknown')
                exact_match = step.get('exact_match', False)

                if exact_match:
                    correct_steps += 1
                else:
                    # Analyze the failure
                    predicted_type = analyze_action_type(predicted)
                    ground_truth_type = analyze_action_type(ground_truth)

                    # Check for hallucinations
                    is_halluc, halluc_element = is_hallucinated_action(predicted, ui_elements)
                    if is_halluc:
                        hallucinations.append({
                            'episode': episode_id,
                            'step': i,
                            'app': app_name,
                            'predicted': predicted,
                            'hallucinated_element': halluc_element,
                            'available_elements': ui_elements
                        })

                    # Track action type mismatches
                    if predicted_type != ground_truth_type:
                        action_type_errors[f"{ground_truth_type} -> {predicted_type}"] += 1

                    # Collect failure pattern
                    failure_patterns[episode_id].append({
                        'step': i,
                        'app': app_name,
                        'predicted': predicted,
                        'ground_truth': ground_truth,
                        'ui_elements': ui_elements,
                        'predicted_type': predicted_type,
                        'ground_truth_type': ground_truth_type,
                        'is_hallucination': is_halluc
                    })

                    # Check for potential goal misinterpretation (first step errors)
                    if i == 0:
                        goal_misinterpretations.append({
                            'episode': episode_id,
                            'predicted': predicted,
                            'ground_truth': ground_truth,
                            'ui_elements': ui_elements
                        })

        except Exception as e:
            print(f"  Error processing {episode_file}: {e}")

    # Generate analysis report
    print(f"\n" + "="*60)
    print(" FAILURE ANALYSIS REPORT")
    print("="*60)

    overall_accuracy = (correct_steps / total_steps * 100) if total_steps > 0 else 0
    print(f" Overall Metrics:")
    print(f"   Episodes analyzed: {episodes_analyzed}")
    print(f"   Total steps: {total_steps}")
    print(f"   Correct steps: {correct_steps}")
    print(f"   Step accuracy: {overall_accuracy:.1f}%")

    print(f"\n Hallucinated Actions: {len(hallucinations)}")
    for h in hallucinations[:5]:  # Show first 5
        print(f"   • {h['episode']}: {h['predicted']} (element '{h['hallucinated_element']}' not in {h['available_elements']})")
    if len(hallucinations) > 5:
        print(f"   ... and {len(hallucinations) - 5} more")

    print(f"\n Action Type Errors:")
    for error_type, count in action_type_errors.most_common(5):
        print(f"   • {error_type}: {count} times")

    print(f"\n Goal Misinterpretations (First Step Failures): {len(goal_misinterpretations)}")
    for gm in goal_misinterpretations[:3]:  # Show first 3
        print(f"   • {gm['episode']}: Predicted '{gm['predicted']}' instead of '{gm['ground_truth']}'")

    print(f"\n UI Reasoning Analysis:")
    click_failures = 0
    navigation_failures = 0
    for episode_id, failures in failure_patterns.items():
        for failure in failures:
            if failure['predicted_type'] == 'CLICK' and failure['ground_truth_type'] == 'CLICK':
                click_failures += 1
            elif failure['predicted_type'] in ['PRESS', 'SCROLL'] or failure['ground_truth_type'] in ['PRESS', 'SCROLL']:
                navigation_failures += 1

    print(f"   • Click element selection errors: {click_failures}")
    print(f"   • Navigation/scroll errors: {navigation_failures}")

    # Save detailed analysis
    analysis_report = {
        'summary': {
            'episodes_analyzed': episodes_analyzed,
            'total_steps': total_steps,
            'correct_steps': correct_steps,
            'step_accuracy': overall_accuracy
        },
        'hallucinations': hallucinations,
        'action_type_errors': dict(action_type_errors),
        'goal_misinterpretations': goal_misinterpretations,
        'failure_patterns': dict(failure_patterns)
    }

    # Ensure results directory exists relative to this file
    output_dir = results_dir if results_dir.exists() else Path(__file__).parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / 'detailed_failure_analysis.json', 'w') as f:
        json.dump(analysis_report, f, indent=2)

    print(f"\n Detailed analysis saved to {output_dir}/detailed_failure_analysis.json")

    return analysis_report


def generate_report_section():
    """Generate the failure analysis section for the report."""
    analysis = analyze_episode_results()

    report_text = f"""
## Detailed Failure Analysis

### Overall Performance
- **Episodes Analyzed**: {analysis['summary']['episodes_analyzed']}
- **Total Steps**: {analysis['summary']['total_steps']}
- **Step Accuracy**: {analysis['summary']['step_accuracy']:.1f}%

### Hallucinated Actions ({len(analysis['hallucinations'])} instances)
LLM agents frequently referenced UI elements that didn't exist on screen:
"""

    for h in analysis['hallucinations'][:3]:
        report_text += f"- **{h['episode']}**: Predicted `{h['predicted']}` but element '{h['hallucinated_element']}' was not in available UI elements\n"

    report_text += f"\n### Action Type Errors\n"
    for error_type, count in list(analysis['action_type_errors'].items())[:3]:
        report_text += f"- **{error_type}**: {count} occurrences\n"

    report_text += f"\n### Goal Misinterpretations\n"
    for gm in analysis['goal_misinterpretations'][:2]:
        report_text += f"- **{gm['episode']}**: Started with `{gm['predicted']}` instead of correct `{gm['ground_truth']}`\n"

    print("\n Report section generated:")
    print(report_text)

    return report_text


if __name__ == "__main__":
    analyze_episode_results()
    print("\n" + "="*60)
    generate_report_section() 