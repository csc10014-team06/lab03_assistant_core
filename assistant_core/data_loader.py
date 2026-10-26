import csv
import json
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

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

class DataLoadError(Exception):
    pass

def load_offices(path: Path) -> dict[str, Office]:
    offices = {}

    try:
        with open(path, newline="", encoding="utf-8") as f:
            data = csv.DictReader(f)

            for line_num, row in enumerate(data, start = 2):
                try:
                    if None in row:
                        raise ValueError("extra column")

                    name = row["name"]
                    if name is None or not name.strip():
                        raise ValueError("empty name")
                    
                    name = name.strip()

                    room = row["room"]
                    if room is None or not room.strip():
                        raise ValueError("empty room")
                    
                    room = room.strip()

                    hours = row["hours"]
                    if hours is None or not hours.strip():
                        raise ValueError("empty hours")

                    hours = hours.strip()

                    office = Office(name, room, hours)
                    offices[name.lower()] = office
                except (ValueError, TypeError, KeyError) as e:
                    raise DataLoadError(f"line {line_num}: {e}") from e
    except FileNotFoundError as e:
        logger.warning("Office file not found: %s", path)
        raise DataLoadError(f"Office file not found: {path}") from e

    return offices

def load_handbook(path: Path) -> list[Rule]:
    rules = []

    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)

            if not isinstance(data, list):
                raise DataLoadError("Handbook must be a list")

            for index, row in enumerate(data, start=1):
                try:
                    if not isinstance(row, dict):
                        raise TypeError("entry must be a dictionary")

                    rule_id = row["id"]
                    if not isinstance(rule_id, str) or not rule_id.strip():
                        raise ValueError("invalid or empty id")
            
                    rule_id = rule_id.strip()

                    title = row["title"]
                    if not isinstance(title, str) or not title.strip():
                        raise ValueError("invalid or empty title")
            
                    title = title.strip()

                    text = row["text"]
                    if not isinstance(text, str) or not text.strip():
                        raise ValueError("invalid or empty text")
            
                    text = text.strip()

                    rule = Rule(rule_id, title, text)
                    rules.append(rule)
                except (ValueError, TypeError, KeyError) as e:
                    raise DataLoadError(f"entry {index}: {e}") from e
    except FileNotFoundError as e:
        logger.warning("Handbook file not found: %s", path)
        raise DataLoadError(f"Handbook file not found: {path}") from e

    except json.JSONDecodeError as e:
        raise DataLoadError(f"Invalid handbook JSON: {e}") from e

    return rules
