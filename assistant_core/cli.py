"""Command-line interface for Assistant Core."""

import argparse
import logging
import sys

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


def run_repl(service=None) -> None:
    """Run interactive REPL loop."""
    print("Study Assistant Core. Type 'quit' to exit.")
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

        if service:
            res = service.handle(prompt)
            print(res)
        else:
            print(f"Echo: {prompt}")


def main(args: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Assistant Core Service CLI")
    parser.add_argument("message", nargs="?", help="Input message to process directly (one-shot mode)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging output")

    parsed_args = parser.parse_args(args)
    setup_logging(debug=parsed_args.debug)

    logger.debug("Starting Assistant Core CLI...")

    if parsed_args.message:
        # One-shot
        logger.info("Executing in one-shot mode")
        print(f"Echo: {parsed_args.message}")
    else:
        # REPL
        run_repl()

    return 0


if __name__ == "__main__":
    sys.exit(main())