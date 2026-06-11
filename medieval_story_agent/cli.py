"""Command-line interface for the medieval story writer agent."""

from __future__ import annotations

import argparse

from .agent import MedievalStoryAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write medieval fantasy stories locally.")
    parser.add_argument("topic", nargs="?", default="", help="Story topic or prompt.")
    parser.add_argument("--language", default="vi", help="Output language code, e.g. vi or en.")
    parser.add_argument(
        "--tone",
        choices=("epic", "dark", "romantic", "humorous"),
        default="epic",
        help="Story tone.",
    )
    parser.add_argument(
        "--length",
        choices=("short", "medium", "long"),
        default="medium",
        help="Story length.",
    )
    parser.add_argument("--protagonist", default="", help="Main character.")
    parser.add_argument("--setting", default="", help="Medieval setting.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    agent = MedievalStoryAgent()
    request = agent.normalize_request(vars(args))
    result = agent.write_story(request)

    print(result["title"])
    print()
    print(result["story"])
    print()
    print("Outline:")
    for item in result["outline"]:
        print(f"- {item}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
