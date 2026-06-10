"""Command-line interface for the interview Q&A agent."""

from __future__ import annotations

import argparse
import sys

from .agent import InterviewAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Practice interview Q&A with a local coaching agent.")
    parser.add_argument(
        "--category",
        choices=("behavioral", "technical", "product"),
        default="behavioral",
        help="Question category to practice.",
    )
    parser.add_argument("--sample", action="store_true", help="Show a sample answer and evaluation.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    agent = InterviewAgent()
    question = agent.next_question(args.category)

    print(f"\nCategory: {question.category}")
    print(f"Question: {question.text}\n")

    if args.sample:
        answer = agent.sample_answer(question)
        print("Sample answer:")
        print(answer)
    else:
        print("Type your answer. Finish with an empty line:\n")
        answer = _read_multiline()

    if not answer.strip():
        print("No answer provided.")
        return 1

    result = agent.evaluate_answer(question, answer)
    print("\nEvaluation")
    print(f"Score: {result['score']}/100 ({result['level']})")
    print(f"Matched signals: {', '.join(result['matched_signals']) or 'none'}")
    print(f"Missing signals: {', '.join(result['missing_signals']) or 'none'}")
    print("Feedback:")
    for item in result["feedback"]:
        print(f"- {item}")

    return 0


def _read_multiline() -> str:
    lines = []
    for line in sys.stdin:
        if not line.strip():
            break
        lines.append(line.rstrip())
    return " ".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
