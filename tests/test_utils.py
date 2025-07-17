import pytest

from src.utils import validate_action, compare_actions


def test_validate_action_click():
    ui = ["Play Store", "Settings"]
    assert validate_action('CLICK("Settings")', ui)
    assert not validate_action('CLICK("Twitter")', ui)


def test_validate_action_nav():
    ui = []
    assert validate_action('PRESS_BACK()', ui)


def test_compare_actions_exact():
    res = compare_actions('CLICK("Settings")', 'CLICK("Settings")')
    assert res["exact_match"]
    assert res["fuzzy_score"] == 100 