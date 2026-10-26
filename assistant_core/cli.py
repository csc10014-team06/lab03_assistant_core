"""Command-line interface for Assistant Core."""

import argparse
import logging
import sys

from assistant_core.config import Settings, load_settings
from assistant_core.data_loader import DataLoadError, load_handbook, load_offices
from assistant_core.llm import DemoLLM
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
    return AssistantService(settings, offices, rules, DemoLLM())


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


def run_repl(service: AssistantService) -> None:
    """Run interactive REPL loop."""
    print(WELCOME_BANNER)
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

        print(service.handle(prompt))


def main(args: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Assistant Core Service CLI")
    parser.add_argument("message", nargs="?", help="Input message to process directly (one-shot mode)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging output")

    parsed_args = parser.parse_args(args)
    settings = load_settings()
    setup_logging(debug=parsed_args.debug or settings.debug)

    logger.debug("Starting Assistant Core CLI...")
    service = build_service(settings)

    if parsed_args.message:
        # One-shot
        logger.debug("Executing in one-shot mode")
        print(service.handle(parsed_args.message))
    else:
        # REPL
        run_repl(service)

    return 0


if __name__ == "__main__":
    sys.exit(main())