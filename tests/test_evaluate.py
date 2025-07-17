from src.agent import AndroidAgent
from src.evaluate import evaluate_episodes


class DummyLLM:
    def generate_action(self, prompt: str):  # noqa: D401
        return 'CLICK("Play Store")'


def test_evaluate_success():
    agent = AndroidAgent(DummyLLM())
    episodes = [
        {
            "episode_id": "test_episode",
            "goal": "Open Play Store",
            "steps": [
                {
                    "observation": {
                        "app_name": "Home Screen",
                        "ui_elements": ["Play Store"],
                        "screen_text": "",
                    },
                    "action": 'CLICK("Play Store")',
                    "step_id": 0,
                }
            ],
        }
    ]

    metrics = evaluate_episodes(agent, episodes, num_episodes=1)
    assert metrics["success_rate"] == 1.0
    assert metrics["step_accuracy"] == 1.0 