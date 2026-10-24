"""Application settings.

Every tunable value that the monolith kept as a module-level constant lives
here, in one place. Values can be overridden with ``ASSISTANT_*`` environment
variables; secrets (the API key) are *only* read from the environment and are
never hard-coded, printed, or included in ``repr()``.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent

ENV_PREFIX = "ASSISTANT_"
_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off", ""}


class ConfigError(ValueError):
    """Raised when an environment variable holds an invalid value."""


@dataclass(frozen=True)
class Settings:
    """Immutable configuration shared by every module of the assistant."""

    credit_rate: int = 450_000  # VND per credit
    retake_multiplier: float = 1.5  # retake credits cost this times the normal rate
    max_credits: int = 30  # handbook rule H26-6.1
    model: str = "gpt-small"
    api_key: str | None = field(default=None, repr=False)
    debug: bool = False
    data_dir: Path = PACKAGE_DIR / "data"
    history_dir: Path = field(default_factory=Path.cwd)

    def __post_init__(self) -> None:
        if self.credit_rate <= 0:
            raise ConfigError(f"credit_rate must be positive, got {self.credit_rate}")
        if self.retake_multiplier <= 0:
            raise ConfigError(
                f"retake_multiplier must be positive, got {self.retake_multiplier}"
            )
        if self.max_credits <= 0:
            raise ConfigError(f"max_credits must be positive, got {self.max_credits}")

    @property
    def offices_path(self) -> Path:
        return self.data_dir / "offices.csv"

    @property
    def handbook_path(self) -> Path:
        return self.data_dir / "handbook.json"


def _parse_int(name: str, raw: str) -> int:
    try:
        return int(raw)
    except ValueError:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from None


def _parse_float(name: str, raw: str) -> float:
    try:
        return float(raw)
    except ValueError:
        raise ConfigError(f"{name} must be a number, got {raw!r}") from None


def _parse_bool(name: str, raw: str) -> bool:
    value = raw.strip().lower()
    if value in _TRUE_VALUES:
        return True
    if value in _FALSE_VALUES:
        return False
    raise ConfigError(f"{name} must be true/false, got {raw!r}")


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build :class:`Settings` from defaults overridden by ``ASSISTANT_*`` variables.

    ``env`` defaults to ``os.environ``; tests pass a plain dict instead.
    """
    if env is None:
        env = os.environ

    def get(key: str) -> str | None:
        return env.get(ENV_PREFIX + key)

    overrides: dict[str, object] = {}
    if (raw := get("CREDIT_RATE")) is not None:
        overrides["credit_rate"] = _parse_int("ASSISTANT_CREDIT_RATE", raw)
    if (raw := get("RETAKE_MULTIPLIER")) is not None:
        overrides["retake_multiplier"] = _parse_float(
            "ASSISTANT_RETAKE_MULTIPLIER", raw
        )
    if (raw := get("MAX_CREDITS")) is not None:
        overrides["max_credits"] = _parse_int("ASSISTANT_MAX_CREDITS", raw)
    if raw := get("MODEL"):
        overrides["model"] = raw
    if raw := get("API_KEY"):
        overrides["api_key"] = raw
    if (raw := get("DEBUG")) is not None:
        overrides["debug"] = _parse_bool("ASSISTANT_DEBUG", raw)
    if raw := get("DATA_DIR"):
        overrides["data_dir"] = Path(raw)
    if raw := get("HISTORY_DIR"):
        overrides["history_dir"] = Path(raw)

    return Settings(**overrides)  # type: ignore[arg-type]
