"""AgentBase runtime entrypoint for the Interview Q&A agent."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from greennode_agentbase import GreenNodeAgentBaseApp, PingStatus, RequestContext
from openai import OpenAI

from interview_agent import InterviewAgent

load_dotenv()

app = GreenNodeAgentBaseApp()
agent = InterviewAgent()


@app.entrypoint
def handler(payload: dict[str, Any], context: RequestContext) -> dict[str, Any]:
    """Handle AgentBase POST /invocations requests."""
    category = str(payload.get("category", "behavioral")).lower()
    answer = str(payload.get("answer") or payload.get("message") or "").strip()
    question_text = str(payload.get("question") or "").strip()

    try:
        question = _question_from_payload(category, question_text)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    if not answer:
        return {
            "status": "success",
            "question": question.text,
            "category": question.category,
            "message": "Send an answer in the 'answer' field to get coaching.",
        }

    local_result = agent.evaluate_answer(question, answer)
    llm_result = _coach_with_llm(question, answer)

    return {
        "status": "success",
        "question": question.text,
        "category": question.category,
        "local_evaluation": local_result,
        "llm_coaching": llm_result,
        "session_id": context.session_id,
    }


@app.ping
def health_check() -> PingStatus:
    """AgentBase health check for GET /health."""
    return PingStatus.HEALTHY


def _question_from_payload(category: str, question_text: str):
    if question_text:
        base = agent.next_question(category)
        return type(base)(
            id="custom",
            category=base.category,
            text=question_text,
            signals=base.signals,
            tips=base.tips,
        )

    return agent.next_question(category)


def _coach_with_llm(question, answer: str) -> dict[str, Any]:
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1")
    model = os.getenv("LLM_MODEL")

    if not api_key or not model:
        return {
            "enabled": False,
            "message": "Set LLM_API_KEY and LLM_MODEL to enable LLM coaching.",
        }

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=agent.coaching_prompt(question, answer),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
    )
    content = response.choices[0].message.content or "{}"

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {"raw": content}

    return {
        "enabled": True,
        "model": model,
        "result": parsed,
    }


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
