"""cli.py — REPL / one-shot entry point and logging setup.

Stub module: implementation owned by han_htg.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from assistant_core.config import load_settings
from assistant_core.data_loader import DataLoadError, load_handbook, load_offices
from assistant_core.llm import DemoLLM
from assistant_core.service import AssistantService


def _build_service(settings) -> AssistantService:
    data_dir = settings.data_dir
    try:
        offices = load_offices(data_dir / "offices.csv")
    except DataLoadError:
        offices = {}
    try:
        rules = load_handbook(data_dir / "handbook.json")
    except DataLoadError:
        rules = []
    llm = DemoLLM(model=settings.model, api_key=settings.api_key)
    return AssistantService(settings, offices, rules, llm)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="assistant_core")
    parser.add_argument("message", nargs="*", help="One-shot message")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.WARNING,
        format="%(levelname)s %(name)s %(message)s",
    )

    settings = load_settings()
    service = _build_service(settings)

    if args.message:
        print(service.handle(" ".join(args.message)))
        return

    print("assistant ready")
    while True:
        try:
            q = input("> ")
        except (EOFError, KeyboardInterrupt):
            break
        if q.strip().lower() == "quit":
            break
        print(service.handle(q))


if __name__ == "__main__":
    main()
