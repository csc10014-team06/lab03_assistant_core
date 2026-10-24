from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from assistant_core.config import PACKAGE_DIR, ConfigError, Settings, load_settings


def test_defaults_match_monolith_constants():
    s = load_settings({})
    assert s.credit_rate == 450_000
    assert s.retake_multiplier == 1.5
    assert s.max_credits == 30
    assert s.model == "gpt-small"


def test_secure_defaults():
    s = load_settings({})
    assert s.api_key is None  # no hard-coded key
    assert s.debug is False  # debug output is opt-in


def test_data_paths_point_into_package():
    s = load_settings({})
    assert s.offices_path == PACKAGE_DIR / "data" / "offices.csv"
    assert s.handbook_path == PACKAGE_DIR / "data" / "handbook.json"


def test_env_overrides(tmp_path):
    s = load_settings(
        {
            "ASSISTANT_CREDIT_RATE": "500000",
            "ASSISTANT_RETAKE_MULTIPLIER": "2",
            "ASSISTANT_MAX_CREDITS": "25",
            "ASSISTANT_MODEL": "other-model",
            "ASSISTANT_API_KEY": "sk-from-env",
            "ASSISTANT_DEBUG": "true",
            "ASSISTANT_DATA_DIR": str(tmp_path),
            "ASSISTANT_HISTORY_DIR": str(tmp_path / "h"),
        }
    )
    assert s.credit_rate == 500_000
    assert s.retake_multiplier == 2.0
    assert s.max_credits == 25
    assert s.model == "other-model"
    assert s.api_key == "sk-from-env"
    assert s.debug is True
    assert s.data_dir == tmp_path
    assert s.history_dir == Path(tmp_path / "h")


def test_unrelated_env_vars_are_ignored():
    assert load_settings({"CREDIT_RATE": "1", "API_KEY": "x"}) == load_settings({})


def test_empty_api_key_means_no_key():
    assert load_settings({"ASSISTANT_API_KEY": ""}).api_key is None


def test_api_key_is_not_in_repr():
    s = load_settings({"ASSISTANT_API_KEY": "sk-secret-123"})
    assert "sk-secret-123" not in repr(s)
    assert "sk-secret-123" not in str(s)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1", True),
        ("TRUE", True),
        ("yes", True),
        ("0", False),
        ("off", False),
        ("", False),
    ],
)
def test_debug_parsing(raw, expected):
    assert load_settings({"ASSISTANT_DEBUG": raw}).debug is expected


@pytest.mark.parametrize(
    ("key", "raw"),
    [
        ("ASSISTANT_CREDIT_RATE", "abc"),
        ("ASSISTANT_CREDIT_RATE", "0"),
        ("ASSISTANT_RETAKE_MULTIPLIER", "x"),
        ("ASSISTANT_MAX_CREDITS", "-5"),
        ("ASSISTANT_DEBUG", "maybe"),
    ],
)
def test_invalid_values_raise_config_error(key, raw):
    with pytest.raises(ConfigError):
        load_settings({key: raw})


def test_settings_are_immutable():
    s = Settings()
    with pytest.raises(FrozenInstanceError):
        s.credit_rate = 1  # type: ignore[misc]


def test_reads_os_environ_by_default(monkeypatch):
    monkeypatch.setenv("ASSISTANT_MAX_CREDITS", "20")
    assert load_settings().max_credits == 20
