"""data_loader.py — Load offices.csv and handbook.json into dataclasses.

Contract from docs/team-plan.md §2 (module owned by vy_th).
"""
from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


class DataLoadError(Exception):
    """Raised when a data file cannot be found or parsed."""


@dataclass(frozen=True)
class Office:
    """An office location with office name, room number, and operating hours."""

    name: str
    room: str
    hours: str


@dataclass(frozen=True)
class Rule:
    """A student handbook regulation with ID, title, and descriptive text."""

    id: str
    title: str
    text: str


def load_offices(path: Path) -> dict[str, Office]:
    """Load offices from a CSV file; dictionary key is lower-cased office name."""
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
        log.warning("Offices file not found: %s", path)
        raise DataLoadError(f"Offices file not found: {path}") from exc
    except (KeyError, csv.Error) as exc:
        raise DataLoadError(f"Malformed offices file: {exc}") from exc
    return offices


def load_handbook(path: Path) -> list[Rule]:
    """Load handbook rules from a JSON file; returns a list of Rule dataclasses."""
    rules: list[Rule] = []
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        for item in data:
            rules.append(
                Rule(
                    id=item["id"],
                    title=item.get("title", ""),
                    text=item["text"],
                )
            )
    except FileNotFoundError as exc:
        log.warning("Handbook file not found: %s", path)
        raise DataLoadError(f"Handbook file not found: {path}") from exc
    except (KeyError, json.JSONDecodeError) as exc:
        raise DataLoadError(f"Malformed handbook file: {exc}") from exc
    return rules
