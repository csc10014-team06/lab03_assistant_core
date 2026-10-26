import pytest

from assistant_core.data_loader import load_offices, DataLoadError

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
