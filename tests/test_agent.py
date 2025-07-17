from src.agent import AndroidAgent


class DummyLLM:
    def __init__(self, action: str):
        self._action = action

    def generate_action(self, prompt: str) -> str:  # noqa: D401
        return self._action


def test_agent_step_valid():
    llm = DummyLLM('CLICK("Play Store")')
    agent = AndroidAgent(llm)
    observation = {
        "app_name": "Home Screen",
        "ui_elements": ["Play Store"],
        "screen_text": "",
    }
    action = agent.step("Open Play Store", observation)
    assert action == 'CLICK("Play Store")' 