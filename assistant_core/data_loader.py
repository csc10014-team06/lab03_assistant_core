import csv
import json
from dataclasses import dataclass
from pathlib import Path


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
        raise DataLoadError(f"Office file not found: {path}") from e

    return offices

