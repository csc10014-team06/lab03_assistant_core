"""Unit tests for Assistant Core CLI."""

from assistant_core.cli import main


def test_cli_one_shot_mode(capsys):
    """Test one-shot execution with an input message."""
    ret = main(["hi"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Hello! I can help with offices, fees and rules." in captured.out


def test_cli_one_shot_uses_service(capsys):
    """One-shot mode answers through AssistantService and the packaged data."""
    assert main(["where is the library"]) == 0
    assert "Library: room B.201, open Mon-Sat 07:00-20:00" in capsys.readouterr().out


def test_cli_repl_quits_on_quit(monkeypatch, capsys):
    """The REPL answers each line and stops on 'quit'."""
    lines = iter(["tuition 10 credits", "quit"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(lines))
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "Your tuition is 4500000 VND" in out
    assert "Goodbye!" in out


def test_cli_debug_flag(caplog):
    """Test that --debug flag activates DEBUG level logging."""
    import logging

    with caplog.at_level(logging.DEBUG):
        ret = main(["test debug", "--debug"])
        assert ret == 0
        assert any("Starting Assistant Core CLI" in record.message for record in caplog.records)