"""Unit tests for Assistant Core CLI."""

from assistant_core.cli import main


def test_cli_one_shot_mode(capsys):
    """Test one-shot execution with an input message."""
    ret = main(["hello assistant"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "hello assistant" in captured.out


def test_cli_debug_flag(caplog):
    """Test that --debug flag activates DEBUG level logging."""
    import logging

    with caplog.at_level(logging.DEBUG):
        ret = main(["test debug", "--debug"])
        assert ret == 0
        assert any("Starting Assistant Core CLI" in record.message for record in caplog.records)