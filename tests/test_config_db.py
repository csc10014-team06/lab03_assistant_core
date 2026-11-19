"""Lab 5 settings: database URL and the secret salt for hashing session ids (owner: long_th)."""

import dataclasses

import pytest

from assistant_core.config import MIN_SALT_LENGTH, ConfigError, Settings, load_settings


def test_db_defaults():
    s = load_settings({})
    assert s.db_url == "sqlite:///assistant.db"
    assert s.hash_salt is None  # no built-in salt: it must come from the environment


def test_db_env_overrides():
    s = load_settings(
        {
            "ASSISTANT_DB_URL": "sqlite:///data/other.db",
            "ASSISTANT_HASH_SALT": "a-long-random-salt",
        }
    )
    assert s.db_url == "sqlite:///data/other.db"
    assert s.hash_salt == "a-long-random-salt"


def test_in_memory_database_url_is_allowed():
    # tests of the database layer use an in-memory database, never assistant.db
    assert Settings(db_url="sqlite://").db_url == "sqlite://"


def test_empty_values_fall_back_to_defaults():
    s = load_settings({"ASSISTANT_DB_URL": "", "ASSISTANT_HASH_SALT": ""})
    assert s.db_url == Settings().db_url
    assert s.hash_salt is None


def test_salt_is_not_in_repr():
    s = load_settings({"ASSISTANT_HASH_SALT": "super-secret-salt"})
    assert s.hash_salt == "super-secret-salt"
    assert "super-secret-salt" not in repr(s)
    assert "super-secret-salt" not in str(s)


def test_unprefixed_variables_are_ignored():
    env = {"DB_URL": "sqlite:///evil.db", "HASH_SALT": "should-not-be-read"}
    assert load_settings(env) == load_settings({})


@pytest.mark.parametrize("url", ["assistant.db", "not a url", "   ", "sqlite"])
def test_invalid_db_url_raises_config_error(url):
    with pytest.raises(ConfigError, match="db_url"):
        load_settings({"ASSISTANT_DB_URL": url})


def test_short_salt_is_rejected():
    with pytest.raises(ConfigError, match="hash_salt"):
        load_settings({"ASSISTANT_HASH_SALT": "x" * (MIN_SALT_LENGTH - 1)})


def test_salt_of_minimum_length_is_accepted():
    assert load_settings({"ASSISTANT_HASH_SALT": "x" * MIN_SALT_LENGTH}).hash_salt == "x" * MIN_SALT_LENGTH


def test_require_hash_salt_returns_the_salt():
    assert Settings(hash_salt="a-long-random-salt").require_hash_salt() == "a-long-random-salt"


def test_require_hash_salt_fails_loudly_when_missing():
    with pytest.raises(ConfigError, match="ASSISTANT_HASH_SALT"):
        Settings().require_hash_salt()


def test_error_message_does_not_leak_the_salt():
    with pytest.raises(ConfigError) as exc:
        Settings(hash_salt="short")
    assert "short" not in str(exc.value)


def test_replace_revalidates():
    # tests build per-test settings with dataclasses.replace (Settings is a frozen dataclass)
    s = dataclasses.replace(Settings(), db_url="sqlite://", hash_salt="test-salt-123")
    assert s.db_url == "sqlite://" and s.hash_salt == "test-salt-123"
    with pytest.raises(ConfigError):
        dataclasses.replace(s, hash_salt="x")


def test_sqlmodel_dependency_is_installed():
    """The Lab 5 database layer builds on SQLModel; fail here, clearly, if the dependency is missing."""
    from sqlalchemy import text
    from sqlmodel import Session, create_engine

    # No table is declared on purpose: SQLModel.metadata is global and must stay clean for the real models.
    with Session(create_engine("sqlite://")) as db:
        assert db.exec(text("SELECT 1")).scalar() == 1
