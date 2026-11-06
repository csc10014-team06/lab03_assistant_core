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
