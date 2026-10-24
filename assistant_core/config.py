"""config.py — Settings and configuration loader.

Stub module: implementation owned by long_th.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class Settings:
    """Application-wide settings; all magic numbers live here."""

    credit_rate: int = 450_000          # VND per credit
    retake_multiplier: float = 1.5
    max_credits: int = 30
    model: str = "gpt-small"
    api_key: str | None = None          # loaded from env ASSISTANT_API_KEY
    debug: bool = False
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent / "data")
    history_dir: Path = field(default_factory=Path.cwd)


def load_settings(env: Mapping[str, str] = os.environ) -> Settings:
    """Load settings from environment variables."""
    return Settings(
        api_key=env.get("ASSISTANT_API_KEY"),
        debug=env.get("ASSISTANT_DEBUG", "").lower() in ("1", "true", "yes"),
    )
