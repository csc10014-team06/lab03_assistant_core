"""Lab 4 settings: the HTTP API fields added to ``Settings`` (owner: long_th)."""

import dataclasses

import pytest

from assistant_core.config import ConfigError, Settings, load_settings


def test_api_defaults():
    s = load_settings({})
    assert s.api_admin_key is None  # no key => admin endpoint stays locked
    assert s.weather_url == "https://api.open-meteo.com/v1/forecast"
    assert s.weather_timeout_s == 3.0
    assert s.campus_lat == 10.7626
    assert s.campus_lon == 106.6822
    assert s.rate_limit_per_min == 30


def test_api_env_overrides():
    s = load_settings(
        {
            "ASSISTANT_API_ADMIN_KEY": "secret-admin",
            "ASSISTANT_WEATHER_URL": "https://example.test/forecast",
            "ASSISTANT_WEATHER_TIMEOUT_S": "1.5",
            "ASSISTANT_CAMPUS_LAT": "21.0",
            "ASSISTANT_CAMPUS_LON": "105.8",
            "ASSISTANT_RATE_LIMIT_PER_MIN": "5",
        }
    )
    assert s.api_admin_key == "secret-admin"
    assert s.weather_url == "https://example.test/forecast"
    assert s.weather_timeout_s == 1.5
    assert s.campus_lat == 21.0
    assert s.campus_lon == 105.8
    assert s.rate_limit_per_min == 5


def test_admin_key_is_not_in_repr():
    s = load_settings({"ASSISTANT_API_ADMIN_KEY": "super-secret-key"})
    assert s.api_admin_key == "super-secret-key"
    assert "super-secret-key" not in repr(s)
    assert "super-secret-key" not in str(s)


def test_empty_admin_key_means_no_key():
    assert load_settings({"ASSISTANT_API_ADMIN_KEY": ""}).api_admin_key is None


def test_empty_weather_url_falls_back_to_default():
    assert load_settings({"ASSISTANT_WEATHER_URL": ""}).weather_url == Settings().weather_url


def test_lab3_variables_without_prefix_are_still_ignored():
    # The starter's un-prefixed names (API_ADMIN_KEY, WEATHER_URL, ...) are not read; only ASSISTANT_*.
    env = {"API_ADMIN_KEY": "x", "WEATHER_URL": "https://evil.test", "RATE_LIMIT_PER_MIN": "1"}
    assert load_settings(env) == load_settings({})


@pytest.mark.parametrize(
    ("key", "raw"),
    [
        ("ASSISTANT_WEATHER_TIMEOUT_S", "abc"),
        ("ASSISTANT_WEATHER_TIMEOUT_S", "0"),
        ("ASSISTANT_WEATHER_TIMEOUT_S", "-1"),
        ("ASSISTANT_WEATHER_TIMEOUT_S", "nan"),
        ("ASSISTANT_CAMPUS_LAT", "north"),
        ("ASSISTANT_CAMPUS_LAT", "90.5"),
        ("ASSISTANT_CAMPUS_LAT", "-91"),
        ("ASSISTANT_CAMPUS_LAT", "nan"),
        ("ASSISTANT_CAMPUS_LON", "east"),
        ("ASSISTANT_CAMPUS_LON", "180.1"),
        ("ASSISTANT_CAMPUS_LON", "-181"),
        ("ASSISTANT_RATE_LIMIT_PER_MIN", "many"),
        ("ASSISTANT_RATE_LIMIT_PER_MIN", "1.5"),
        ("ASSISTANT_RATE_LIMIT_PER_MIN", "0"),
        ("ASSISTANT_RATE_LIMIT_PER_MIN", "-3"),
    ],
)
def test_invalid_api_values_raise_config_error(key, raw):
    with pytest.raises(ConfigError):
        load_settings({key: raw})


def test_error_message_names_the_variable():
    with pytest.raises(ConfigError, match="ASSISTANT_RATE_LIMIT_PER_MIN"):
        load_settings({"ASSISTANT_RATE_LIMIT_PER_MIN": "many"})


def test_boundary_coordinates_are_valid():
    s = Settings(campus_lat=-90, campus_lon=180)
    assert (s.campus_lat, s.campus_lon) == (-90, 180)


def test_replace_overrides_a_field_and_revalidates():
    # tests/test_api.py builds its per-test settings this way (Settings is a frozen dataclass).
    s = dataclasses.replace(Settings(), api_admin_key="secret-admin", rate_limit_per_min=5)
    assert s.api_admin_key == "secret-admin" and s.rate_limit_per_min == 5
    with pytest.raises(ConfigError):
        dataclasses.replace(s, rate_limit_per_min=0)
