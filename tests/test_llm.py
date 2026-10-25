
"""Unit tests for the LLM interface and implementations."""

import logging

import pytest

from assistant_core.llm import DemoLLM, FakeLLM, LLMClient, LLMError


def test_fake_llm_is_deterministic_and_records_prompt() -> None:
    client = FakeLLM("fixed answer")

    assert isinstance(client, LLMClient)
    assert client.complete("hello") == "fixed answer"
    assert client.complete("another prompt") == "fixed answer"
    assert client.prompts == ["hello", "another prompt"]


def test_demo_llm_preserves_response_format() -> None:
    client = DemoLLM(rng=lambda: 0.5, sleep_fn=lambda _: None)

    assert client.complete("Question: hello") == (
        "Here is what I found: Question: hello"
    )


def test_demo_llm_truncates_response_to_last_120_prompt_characters() -> None:
    prompt = "x" * 200
    client = DemoLLM(rng=lambda: 0.5, sleep_fn=lambda _: None)

    assert client.complete(prompt) == (
        "Here is what I found: " + prompt[-120:]
    )


def test_demo_llm_raises_llm_error_on_timeout() -> None:
    client = DemoLLM(rng=lambda: 0.01, sleep_fn=lambda _: None)

    with pytest.raises(LLMError, match="LLM timeout"):
        client.complete("hello")


def test_demo_llm_uses_injected_sleep() -> None:
    delays: list[float] = []
    client = DemoLLM(
        rng=lambda: 0.5,
        sleep_fn=delays.append,
        delay_seconds=0.75,
    )

    client.complete("hello")

    assert delays == [0.75]


def test_demo_llm_logs_truncated_prompt_at_debug(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = logging.getLogger("test.demo_llm")
    client = DemoLLM(
        rng=lambda: 0.5,
        sleep_fn=lambda _: None,
        logger=logger,
    )

    with caplog.at_level(logging.DEBUG, logger="test.demo_llm"):
        client.complete("P" * 100)

    assert "P" * 60 in caplog.text
    assert "P" * 61 not in caplog.text
    assert "api_key" not in caplog.text.lower()


def test_demo_llm_does_not_log_prompt_at_info(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = logging.getLogger("test.demo_llm.quiet")
    client = DemoLLM(
        rng=lambda: 0.5,
        sleep_fn=lambda _: None,
        logger=logger,
    )

    with caplog.at_level(logging.INFO, logger="test.demo_llm.quiet"):
        client.complete("private prompt")

    assert "private prompt" not in caplog.text


@pytest.mark.parametrize("probability", [-0.1, 1.1])
def test_demo_llm_rejects_invalid_timeout_probability(
    probability: float,
) -> None:
    with pytest.raises(ValueError, match="timeout_probability"):
        DemoLLM(timeout_probability=probability)


def test_demo_llm_rejects_negative_delay() -> None:
    with pytest.raises(ValueError, match="delay_seconds"):
        DemoLLM(delay_seconds=-0.1)
