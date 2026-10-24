"""data_loader.py — load offices.csv and handbook.json into dataclasses.

Stub module: implementation owned by vy_th.
"""
from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


class DataLoadError(Exception):
    """Raised when a required data file cannot be loaded or is malformed."""


@dataclass(frozen=True)
class Office:
    name: str
    room: str
    hours: str


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    text: str


def load_offices(path: Path) -> dict[str, Office]:
    """Load offices.csv; key is lower-cased office name.

    Raises DataLoadError if the file is missing or malformed.
    """
    offices: dict[str, Office] = {}
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                name = row["name"].strip()
                offices[name.lower()] = Office(
                    name=name,
                    room=row["room"].strip(),
                    hours=row["hours"].strip(),
                )
    except FileNotFoundError as exc:
        log.warning("offices file not found: %s", path)
        raise DataLoadError(f"offices file not found: {path}") from exc
    except (KeyError, csv.Error) as exc:
        raise DataLoadError(f"malformed offices file: {exc}") from exc
    return offices


def load_handbook(path: Path) -> list[Rule]:
    """Load handbook.json; returns a list of Rule dataclasses.

    Raises DataLoadError if the file is missing or malformed.
    """
    rules: list[Rule] = []
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        for entry in data:
            rules.append(Rule(
                id=entry["id"],
                title=entry.get("title", ""),
                text=entry["text"],
            ))
    except FileNotFoundError as exc:
        log.warning("handbook file not found: %s", path)
        raise DataLoadError(f"handbook file not found: {path}") from exc
    except (KeyError, json.JSONDecodeError) as exc:
        raise DataLoadError(f"malformed handbook file: {exc}") from exc
    return rules
