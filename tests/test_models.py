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


def test_respond_greeting():
    from assistant_core.config import Settings
    from assistant_core.llm import FakeLLM
    from assistant_core.service import AssistantService

    service = AssistantService(Settings(), {}, [], FakeLLM())
    resp = service.respond(Message(text="hello"))
    assert resp.intent == Intent.GREETING
    assert resp.answer == "Hello! I can help with offices, fees and rules."
    assert resp.sources == []
    assert resp.degraded is False


def test_respond_fee_with_thousands_separator():
    from assistant_core.config import Settings
    from assistant_core.llm import FakeLLM
    from assistant_core.service import AssistantService

    # 18 credits * 450,000 + 2 retakes * 1.5 * 450,000 = 8,100,000 + 1,350,000 = 9,450,000
    service = AssistantService(
        Settings(credit_rate=450_000, retake_multiplier=1.5, max_credits=30),
        {},
        [],
        FakeLLM(),
    )
    resp = service.respond(Message(text="tuition for 18 credits and 2 retake"))
    assert resp.intent == Intent.FEE
    assert resp.answer == "Your tuition is 9,450,000 VND."
    assert resp.sources == []
    assert resp.degraded is False


def test_respond_fee_zero_credits():
    from assistant_core.config import Settings
    from assistant_core.llm import FakeLLM
    from assistant_core.service import AssistantService

    service = AssistantService(Settings(), {}, [], FakeLLM())
    resp = service.respond(Message(text="what is the tuition fee?"))
    assert resp.intent == Intent.FEE
    assert resp.answer == "How many credits?"


def test_respond_fee_too_many_credits():
    from assistant_core.config import Settings
    from assistant_core.llm import FakeLLM
    from assistant_core.service import AssistantService

    service = AssistantService(Settings(max_credits=30), {}, [], FakeLLM())
    resp = service.respond(Message(text="tuition for 35 credits"))
    assert resp.intent == Intent.FEE
    assert resp.answer == "too many credits"


def test_respond_unknown():
    from assistant_core.config import Settings
    from assistant_core.llm import FakeLLM
    from assistant_core.service import AssistantService

    service = AssistantService(Settings(), {}, [], FakeLLM())
    resp = service.respond(Message(text="random unrelated query"))
    assert resp.intent == Intent.UNKNOWN
    assert resp.answer == "Sorry I dont know"
    assert resp.sources == []
    assert resp.degraded is False


def test_respond_office():
    from assistant_core.config import Settings
    from assistant_core.data_loader import Office
    from assistant_core.llm import FakeLLM
    from assistant_core.service import AssistantService

    offices_dict = {
        "library": Office(name="Library", room="B.201", hours="Mon-Sat 07:00-20:00")
    }
    service = AssistantService(Settings(), offices_dict, [], FakeLLM())
    resp = service.respond(Message(text="where is the library"))
    assert resp.intent == Intent.OFFICE
    assert resp.answer == "Library: room B.201, open Mon-Sat 07:00-20:00"
    assert resp.sources == []
    assert resp.degraded is False


def test_respond_rule_with_source():
    from assistant_core.config import Settings
    from assistant_core.data_loader import Rule
    from assistant_core.llm import FakeLLM
    from assistant_core.service import AssistantService

    rule = Rule(
        id="academic-retake",
        title="Course Retake Policy",
        text="Students may retake a course up to 2 times.",
    )
    llm = FakeLLM(response="Yes, you can retake up to two times.")
    service = AssistantService(Settings(), {}, [rule], llm)

    resp = service.respond(Message(text="can I retake a course?"))
    assert resp.intent == Intent.RULE
    # answer must NOT contain (source: ...) suffix
    assert "(source:" not in resp.answer
    assert resp.answer == "Yes, you can retake up to two times."
    assert len(resp.sources) == 1
    assert resp.sources[0].id == "academic-retake"
    assert resp.sources[0].title == "Course Retake Policy"
    assert resp.degraded is False


def test_respond_rule_llm_failure_degraded():
    from assistant_core.config import Settings
    from assistant_core.data_loader import Rule
    from assistant_core.llm import LLMClient, LLMError
    from assistant_core.service import AssistantService

    class FailingLLM(LLMClient):
        def complete(self, prompt: str) -> str:
            raise LLMError("API timed out")

    rule = Rule(
        id="academic-retake",
        title="Course Retake Policy",
        text="Students may retake a course up to 2 times.",
    )
    service = AssistantService(Settings(), {}, [rule], FailingLLM())

    resp = service.respond(Message(text="can I retake a course?"))
    assert resp.intent == Intent.RULE
    # On LLM failure, fallback to raw rule text without (source: ...) and degraded=True
    assert "(source:" not in resp.answer
    assert resp.answer == "Students may retake a course up to 2 times."
    assert len(resp.sources) == 1
    assert resp.sources[0].id == "academic-retake"
    assert resp.sources[0].title == "Course Retake Policy"
    assert resp.degraded is True
