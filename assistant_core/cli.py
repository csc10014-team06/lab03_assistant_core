"""Command-line interface for Assistant Core."""

import argparse
import logging
import sys

from assistant_core.config import ANSWER_PATHS, Settings, load_settings
from assistant_core.data_loader import DataLoadError, load_handbook, load_offices
from assistant_core.llm import DemoLLM, make_draft_provider
from assistant_core.models import Response
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.index import KBError, KBIndex
from assistant_core.service import AssistantService

logger = logging.getLogger("assistant_core")


def setup_logging(debug: bool = False) -> None:
    """Configure logging format and level."""
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)

    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)


def build_service(settings: Settings) -> AssistantService:
    """Load the data files and wire up the service; missing data is logged, not fatal."""
    try:
        offices = load_offices(settings.offices_path)
    except DataLoadError as exc:
        logger.warning("Continuing without offices: %s", exc)
        offices = {}
    try:
        rules = load_handbook(settings.handbook_path)
    except DataLoadError as exc:
        logger.warning("Continuing without handbook: %s", exc)
        rules = []
    return AssistantService(settings, offices, rules, DemoLLM(), rag=build_rag(settings))


def build_rag(settings: Settings) -> RagAnswerer | None:
    """Load the knowledge base and the draft provider; without a KB the assistant uses rules only."""
    try:
        index = KBIndex.from_dir(settings.kb_dir)
    except KBError as exc:
        logger.warning("Continuing without knowledge base (rules only): %s", exc)
        return None
    provider = make_draft_provider(settings.llm_provider, settings.llm_model, settings.ollama_url)
    return RagAnswerer(index, provider, min_score=settings.retrieval_min_score, k=settings.retrieval_k)


_COMMANDS = ("history", "stats", "save")


def format_response(resp: Response) -> str:
    """One line for the terminal: the answer plus the cited chunk ids, like the rules path does."""
    if resp.sources:
        return f"{resp.answer} (source: {', '.join(s.id for s in resp.sources)})"
    return resp.answer


def answer(service: AssistantService, text: str, path: str) -> str:
    """Rules path, commands, greetings, fees and offices go through handle() (unchanged output)."""
    if path == "rules" or text.lower().split()[:1] in ([c] for c in _COMMANDS) or service.routes_to_rules(text):
        return service.handle(text)
    return format_response(service.ask(text, path))


WELCOME_BANNER = """\
============================================================
Study Assistant Core
Ask me questions about:
  * Offices:   e.g. 'where is the library?', 'health service'
  * Tuition:   e.g. 'tuition 18 credits 2 retakes', 'fees'
  * Handbook:  e.g. 'exam absence', 'thesis rule', 'max credits'
  * Commands:  'stats', 'save <filename>', 'quit'
Type 'quit' or 'exit' to exit.
============================================================\
"""


def run_repl(service: AssistantService, path: str = "rules") -> None:
    """Run interactive REPL loop."""
    print(WELCOME_BANNER)
    print(f"(answer path: {path})")
    while True:
        try:
            prompt = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not prompt:
            continue
        if prompt.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break

        print(answer(service, prompt, path))


def main(args: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Assistant Core Service CLI")
    parser.add_argument("message", nargs="?", help="Input message to process directly (one-shot mode)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging output")
    parser.add_argument(
        "--path",
        choices=ANSWER_PATHS,
        default=None,
        help="Answering path (default: ASSISTANT_ANSWER_PATH, or 'llm'): rules only, KB retrieval, or KB + model",
    )

    parsed_args = parser.parse_args(args)
    settings = load_settings()
    setup_logging(debug=parsed_args.debug or settings.debug)

    logger.debug("Starting Assistant Core CLI...")
    service = build_service(settings)
    path = parsed_args.path or settings.answer_path

    if parsed_args.message:
        # One-shot
        logger.debug("Executing in one-shot mode (path=%s)", path)
        print(answer(service, parsed_args.message, path))
    else:
        # REPL
        run_repl(service, path)

    return 0


def entrypoint() -> int:
    """Console-script / ``python -m`` entry: read ``.env`` (never overriding real env vars), then run."""
    from dotenv import load_dotenv

    load_dotenv(override=False)
    return main()


if __name__ == "__main__":
    sys.exit(entrypoint())