import pytest

from assistant_core.data_loader import load_offices, DataLoadError
from assistant_core.data_loader import load_handbook

def test_load_offices_valid(tmp_path):
    path = tmp_path / "offices.csv"

    path.write_text(
        "name,room,hours\n"
        "Library,B.201,Mon-Sat 07:00-20:00\n",
        encoding="utf-8"
    )

    offices = load_offices(path)

    assert "library" in offices
    assert offices["library"].name == "Library"
    assert offices["library"].room == "B.201"
    assert offices["library"].hours == "Mon-Sat 07:00-20:00"

def test_load_offices_missing_file(tmp_path):
    path = tmp_path / "missing.csv"

    with pytest.raises(DataLoadError):
        load_offices(path)

def test_load_offices_empty_room(tmp_path):
    path = tmp_path / "offices.csv"

    path.write_text(
        "name,room,hours\n"
        "Library,B.201,Mon-Sat 07:00-20:00\n"
        "Training Office,,Mon-Fri 08:00-17:00\n",
        encoding="utf-8"
    )

    with pytest.raises(DataLoadError, match="line 3: empty room"):
        load_offices(path)

def test_load_handbook_valid(tmp_path):
    path = tmp_path / "handbook.json"

    path.write_text(
        '[{"id": "H26-4.2", "title": "Retaking a course", '
        '"text": "Students may retake a course."}]',
        encoding="utf-8"
    )

    rules = load_handbook(path)

    assert len(rules) == 1
    assert rules[0].id == "H26-4.2"
    assert rules[0].title == "Retaking a course"

def test_load_handbook_invalid_json(tmp_path):
    path = tmp_path / "handbook.json"

    path.write_text(
        '[{"id": "H26-4.2",}]',
        encoding="utf-8"
    )

    with pytest.raises(DataLoadError, match="Invalid handbook JSON"):
        load_handbook(path)

def test_load_handbook_missing_text(tmp_path):
    path = tmp_path / "handbook.json"

    path.write_text(
        '[{"id": "H26-4.2", "title": "Retaking", "text": "Some rules"},'
        '{"id": "H26-5.3", "title": "Thesis registration"}]',
        encoding="utf-8"
    )

    with pytest.raises(DataLoadError, match="entry 2:"):
        load_handbook(path)

def test_load_handbook_missing_file(tmp_path):
    path = tmp_path / "missing.json"

    with pytest.raises(DataLoadError):
        load_handbook(path)

def test_load_handbook_not_list(tmp_path):
    path = tmp_path / "handbook.json"

    path.write_text("{}", encoding="utf-8")

    with pytest.raises(DataLoadError, match="Handbook must be a list"):
        load_handbook(path)
