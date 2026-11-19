"""service.py — AssistantService: routing, history, stats, save_history.

Owner: nhat_dm

Responsibilities
----------------
* Replace the monolith's handle(), stats(), save_history() functions and the
  ``history`` global with a self-contained AssistantService class.
* Route each message to the right handler (fees / office / handbook / LLM).
* On LLM failure, fall back to returning the raw rule text (same as today).
* Fix the path-traversal bug in save_history: restrict output to history_dir.
* Return a plain dict from stats(); formatting is the CLI's job.

Design notes
------------
* All intent detection is done through the public functions from fees.py,
  offices.py, and handbook.py — no duplicated keyword logic here.
* The LLM client is injected so tests can pass FakeLLM without network calls.
* No module-level mutable state; every instance carries its own history list.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from assistant_core.config import Settings
from assistant_core.data_loader import Office, Rule
from assistant_core.fees import FeeQuery, TooManyCreditsError, compute_tuition, parse_fee_query
from assistant_core.handbook import best_rule
from assistant_core.llm import LLMClient, LLMError
from assistant_core.models import Intent, Message, Response, Source
from assistant_core.offices import find_office

log = logging.getLogger(__name__)

# Words that reliably indicate a fee / tuition intent (whole-word match).
# Using re.search with \b avoids 'coffee' triggering the fee branch.
_FEE_PATTERN = re.compile(r"\b(fees?|tuition)\b", re.IGNORECASE)

# Words that indicate rule/handbook intent (used in stats only).
_RULE_KEYWORDS = frozenset({"thesis", "retake", "exam", "credit"})


class AssistantService:
    """High-level service that handles one message at a time.

    Parameters
    ----------
    settings:
        Application settings (credit rates, paths, …).
    offices:
        Mapping of lower-cased office name → Office dataclass.
    rules:
        List of Rule dataclasses loaded from the handbook.
    llm:
        Any object satisfying the LLMClient protocol.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(
        self,
        settings: Settings,
        offices: dict[str, Office],
        rules: list[Rule],
        llm: LLMClient,
    ) -> None:
        self._settings = settings
        self._offices = offices
        self._rules = rules
        self._llm = llm
        self._history: list[str] = []          # replaces the global ``history``

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handle(self, message: str) -> str:
        """Process *message* and return the assistant's response.

        The message is appended to history *before* routing so that even
        messages that fail mid-way are recorded (consistent with the monolith).
        """
        self._history.append(message)
        m = message.lower().strip()

        # --- built-in commands -------------------------------------------
        if m == "":
            return "empty"

        if m in {"hi", "hello", "hey", "xin chao"}:
            return "Hello! I can help with offices, fees and rules."

        if m == "history":
            return "\n".join(self._history)

        if m == "stats":
            d = self.stats()
            return (
                f"fee={d['fee']} office={d['office']} "
                f"rule={d['rule']} other={d['other']}"
            )

        if m.startswith("save"):
            parts = message.split()
            fname = parts[-1] if len(parts) > 1 else "history.txt"
            saved_path = self.save_history(fname)
            log.debug("saved %d lines to %s", len(self._history), saved_path)
            return "saved"

        # --- fee intent --------------------------------------------------
        if _FEE_PATTERN.search(m):
            return self._handle_fee(message)

        # --- office intent -----------------------------------------------
        office = find_office(message, self._offices)
        if office is not None:
            return f"{office.name}: room {office.room}, open {office.hours}"

        # --- handbook + LLM ----------------------------------------------
        rule = best_rule(message, self._rules)
        if rule is not None:
            return self._handle_rule(rule, message)

        return "Sorry I dont know"

    def respond(self, msg: Message) -> Response:
        """Process a structured *msg* and return a typed :class:`Response`.

        Used by the HTTP API. Unlike handle():
        - Fee answers format amounts with commas: ``f"Your tuition is {total:,} VND."``
        - Rule answers omit the ``(source: ...)`` suffix and populate ``sources``.
        - LLM errors set ``degraded=True`` and fall back to the raw rule text.
        - CLI commands (history, stats, save) are not executed; they are treated
          as normal text queries to avoid exposing internal state over HTTP.
        """
        m = msg.text.lower().strip()

        if m in {"hi", "hello", "hey", "xin chao"}:
            return Response(
                answer="Hello! I can help with offices, fees and rules.",
                intent=Intent.GREETING,
                sources=[],
                degraded=False,
            )

        if _FEE_PATTERN.search(m):
            return self._respond_fee(msg.text)

        office = find_office(msg.text, self._offices)
        if office is not None:
            return Response(
                answer=f"{office.name}: room {office.room}, open {office.hours}",
                intent=Intent.OFFICE,
                sources=[],
                degraded=False,
            )

        rule = best_rule(msg.text, self._rules)
        if rule is not None:
            return self._respond_rule(rule, msg.text)

        return Response(
            answer="Sorry I dont know",
            intent=Intent.UNKNOWN,
            sources=[],
            degraded=False,
        )

    def offices(self) -> list[Office]:
        """Return all offices sorted by name.

        Delegates to offices.all_offices (truyen_lp's H1), falling back to
        a sorted list of offices when all_offices is not yet available.
        """
        try:
            from assistant_core.offices import all_offices  # type: ignore[attr-defined]

            return all_offices(self._offices)
        except (ImportError, AttributeError):
            return sorted(self._offices.values(), key=lambda o: o.name)

    def stats(self) -> dict[str, int]:
        """Return intent counts for all messages seen so far.

        Keys: 'fee', 'office', 'rule', 'other'.
        Formatting is left to the caller (e.g. cli.py).
        """
        counts: dict[str, int] = {"fee": 0, "office": 0, "rule": 0, "other": 0}
        for msg in self._history:
            lower = msg.lower()
            if _FEE_PATTERN.search(lower):
                counts["fee"] += 1
            elif find_office(msg, self._offices) is not None:
                counts["office"] += 1
            elif any(w in lower for w in _RULE_KEYWORDS):
                counts["rule"] += 1
            else:
                counts["other"] += 1
        return counts

    def save_history(self, filename: str) -> Path:
        """Write history to *filename* inside history_dir and return the path.

        Security: the filename is stripped of path separators so that a
        malicious input like ``save ../../etc/passwd`` cannot escape
        history_dir.  Only the basename is used.
        """
        safe_name = Path(filename).name          # strip any directory component
        if not safe_name:
            safe_name = "history.txt"
        out_path = self._settings.history_dir / safe_name
        with open(out_path, "w", encoding="utf-8") as fh:
            for msg in self._history:
                fh.write(msg + "\n")
        return out_path

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _handle_fee(self, message: str) -> str:
        """Parse and compute tuition; return a user-facing string."""
        query: FeeQuery = parse_fee_query(message)
        if query.credits == 0:
            return "How many credits?"
        try:
            total = compute_tuition(query, self._settings)
        except TooManyCreditsError:
            return "too many credits"
        return f"Your tuition is {total} VND"

    def _respond_fee(self, message: str) -> Response:
        """Parse and compute tuition formatted with thousands separators for HTTP API."""
        query: FeeQuery = parse_fee_query(message)
        if query.credits == 0:
            return Response(
                answer="How many credits?",
                intent=Intent.FEE,
                sources=[],
                degraded=False,
            )
        try:
            total = compute_tuition(query, self._settings)
        except TooManyCreditsError:
            return Response(
                answer="too many credits",
                intent=Intent.FEE,
                sources=[],
                degraded=False,
            )
        return Response(
            answer=f"Your tuition is {total:,} VND.",
            intent=Intent.FEE,
            sources=[],
            degraded=False,
        )

    def _handle_rule(self, rule: Rule, original_message: str) -> str:
        """Ask the LLM about *rule*; fall back to raw text on failure."""
        prompt = f"Answer using this rule: {rule.text} Question: {original_message}"
        try:
            answer = self._llm.complete(prompt)
            return f"{answer} (source: {rule.id})"
        except LLMError as exc:
            log.warning("LLM failed, falling back to rule text: %s", exc)
            return f"{rule.text} (source: {rule.id})"

    def _respond_rule(self, rule: Rule, original_message: str) -> Response:
        """Ask the LLM about *rule*; on failure fall back to raw rule text with degraded=True."""
        prompt = f"Answer using this rule: {rule.text} Question: {original_message}"
        source = Source(id=rule.id, title=rule.title)
        try:
            answer = self._llm.complete(prompt)
            return Response(
                answer=answer,
                intent=Intent.RULE,
                sources=[source],
                degraded=False,
            )
        except LLMError as exc:
            log.warning("LLM failed, falling back to rule text: %s", exc)
            return Response(
                answer=rule.text,
                intent=Intent.RULE,
                sources=[source],
                degraded=True,
            )
