"""Core interview Q&A coaching logic."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Iterable

from .questions import QUESTION_BANK


@dataclass(frozen=True)
class Question:
    """A normalized interview question."""

    id: str
    category: str
    text: str
    signals: tuple[str, ...]
    tips: tuple[str, ...]


class InterviewAgent:
    """A lightweight interview practice agent.

    The agent intentionally avoids network calls, making it useful in local demos
    and hackathon settings where API keys may not be available.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._random = random.Random(seed)
        self._questions = self._load_questions()

    @property
    def categories(self) -> tuple[str, ...]:
        return tuple(QUESTION_BANK.keys())

    def next_question(self, category: str = "behavioral") -> Question:
        category = category.lower().strip()
        if category not in QUESTION_BANK:
            available = ", ".join(self.categories)
            raise ValueError(f"Unknown category '{category}'. Choose one of: {available}.")

        return self._random.choice(self._questions[category])

    def evaluate_answer(self, question: Question, answer: str) -> dict[str, object]:
        words = self._tokenize(answer)
        matched_signals = self._matched_signals(question.signals, answer)
        length_score = self._length_score(len(words))
        signal_score = round((len(matched_signals) / max(len(question.signals), 1)) * 100)
        structure_score = self._structure_score(answer)
        score = round((length_score * 0.25) + (signal_score * 0.5) + (structure_score * 0.25))

        return {
            "score": score,
            "level": self._level(score),
            "matched_signals": matched_signals,
            "missing_signals": [signal for signal in question.signals if signal not in matched_signals],
            "feedback": self._feedback(score, matched_signals, question.tips),
        }

    def sample_answer(self, question: Question) -> str:
        if question.category == "behavioral":
            return (
                "Situation: In my last project, a key stakeholder was worried about delivery risk. "
                "Task: I needed to align expectations while keeping the team focused. "
                "Action: I clarified priorities, shared a weekly progress view, and escalated blockers early. "
                "Result: We shipped the critical scope on time and reduced late change requests."
            )

        if question.category == "technical":
            return (
                "I would first clarify traffic, latency, and consistency requirements. "
                "For a distributed payment API, I would use a token bucket backed by Redis, with per-user and per-merchant limits. "
                "I would define behavior for Redis failure, monitor rejection rate and latency, and test edge cases under load."
            )

        return (
            "I would start by measuring the current funnel and identifying the largest dropoff. "
            "Then I would segment users, form hypotheses, and run experiments that balance conversion, risk, and compliance. "
            "Prioritization would be based on impact, effort, confidence, and stakeholder alignment."
        )

    def coaching_prompt(self, question: Question, answer: str) -> list[dict[str, str]]:
        """Build messages for an OpenAI-compatible chat model."""
        local_evaluation = self.evaluate_answer(question, answer)
        return [
            {
                "role": "system",
                "content": (
                    "You are an interview coach for software, product, and fintech candidates. "
                    "Give concise, practical feedback. Be specific, honest, and encouraging. "
                    "Return a JSON object with keys: score, summary, strengths, improvements, revised_answer. "
                    "Do not include markdown fences."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Category: {question.category}\n"
                    f"Question: {question.text}\n"
                    f"Expected signals: {', '.join(question.signals)}\n"
                    f"Candidate answer: {answer}\n"
                    f"Local rubric score: {local_evaluation['score']}/100\n"
                    f"Local matched signals: {', '.join(local_evaluation['matched_signals']) or 'none'}\n"
                    "Coach this answer and provide a stronger revised answer."
                ),
            },
        ]

    def _load_questions(self) -> dict[str, list[Question]]:
        return {
            category: [
                Question(
                    id=item["id"],
                    category=category,
                    text=item["question"],
                    signals=tuple(item["signals"]),
                    tips=tuple(item["tips"]),
                )
                for item in items
            ]
            for category, items in QUESTION_BANK.items()
        }

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"[a-zA-Z0-9']+", text.lower())

    def _matched_signals(self, signals: Iterable[str], answer: str) -> list[str]:
        normalized = answer.lower()
        return [signal for signal in signals if signal.lower() in normalized]

    def _length_score(self, word_count: int) -> int:
        if word_count < 25:
            return 35
        if word_count < 60:
            return 70
        if word_count <= 180:
            return 100
        return 75

    def _structure_score(self, answer: str) -> int:
        lowered = answer.lower()
        markers = ["situation", "task", "action", "result", "first", "then", "finally"]
        hits = sum(1 for marker in markers if marker in lowered)
        return min(100, 35 + hits * 18)

    def _level(self, score: int) -> str:
        if score >= 85:
            return "strong"
        if score >= 65:
            return "solid"
        if score >= 45:
            return "needs work"
        return "thin"

    def _feedback(self, score: int, matched_signals: list[str], tips: tuple[str, ...]) -> list[str]:
        feedback = []
        if score >= 85:
            feedback.append("Strong answer. Keep the structure tight and make the impact easy to remember.")
        elif score >= 65:
            feedback.append("Good foundation. Add sharper evidence, tradeoffs, or measurable results.")
        else:
            feedback.append("The answer needs more substance. Add context, actions, and outcomes.")

        if not matched_signals:
            feedback.append("Use more role-relevant keywords so the interviewer can see the signal quickly.")

        feedback.extend(tips)
        return feedback
