"""Tests for assistant_core.models and AssistantService.respond / offices.

Owner: nhat_dm
"""
import pytest
from pydantic import ValidationError

from assistant_core.models import Intent, Message, Response, Source


def test_intent_values():
    assert Intent.GREETING == "greeting"
    assert Intent.FEE == "fee"
    assert Intent.OFFICE == "office"
    assert Intent.RULE == "rule"
    assert Intent.UNKNOWN == "unknown"


def test_message_valid():
    msg = Message(text="hello")
    assert msg.text == "hello"
    assert msg.session_id == "local"

    msg_custom = Message(text="where is the library", session_id="user-42")
    assert msg_custom.session_id == "user-42"


def test_message_validation_empty():
    with pytest.raises(ValidationError):
        Message(text="")


def test_message_validation_too_long():
    with pytest.raises(ValidationError):
        Message(text="a" * 2001)


def test_source_model():
    source = Source(id="rule-1", title="Retake Policy")
    assert source.id == "rule-1"
    assert source.title == "Retake Policy"
    assert source.model_dump() == {"id": "rule-1", "title": "Retake Policy"}


def test_response_defaults():
    resp = Response(answer="Hello", intent=Intent.GREETING)
    assert resp.answer == "Hello"
    assert resp.intent == Intent.GREETING
    assert resp.sources == []
    assert resp.degraded is False
    assert resp.model_dump()["sources"] == []
    assert resp.model_dump()["degraded"] is False


def test_service_offices_standin():
    from assistant_core.config import Settings
    from assistant_core.data_loader import Office
    from assistant_core.llm import FakeLLM
    from assistant_core.service import AssistantService

    offices_dict = {
        "registrar": Office(name="Registrar", room="B202", hours="8-12"),
        "library": Office(name="Library", room="A101", hours="8-17"),
        "academic affairs": Office(name="Academic Affairs", room="C303", hours="9-16"),
    }
    service = AssistantService(Settings(), offices_dict, [], FakeLLM())
    result = service.offices()
    assert [o.name for o in result] == ["Academic Affairs", "Library", "Registrar"]


def test_service_offices_delegates_to_all_offices(monkeypatch):
    import assistant_core.offices as offices_mod
    from assistant_core.config import Settings
    from assistant_core.data_loader import Office
    from assistant_core.llm import FakeLLM
    from assistant_core.service import AssistantService

    offices_dict = {"library": Office(name="Library", room="A101", hours="8-17")}
    sentinel_office = Office(name="Custom Sorted", room="X", hours="Y")

    def mock_all_offices(d):
        assert d is offices_dict
        return [sentinel_office]

    monkeypatch.setattr(offices_mod, "all_offices", mock_all_offices, raising=False)
    service = AssistantService(Settings(), offices_dict, [], FakeLLM())
    assert service.offices() == [sentinel_office]
