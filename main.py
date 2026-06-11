"""AgentBase runtime entrypoint for the Medieval Story Writer agent."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from greennode_agentbase import GreenNodeAgentBaseApp, PingStatus, RequestContext
from openai import OpenAI

from medieval_story_agent import MedievalStoryAgent

load_dotenv()

app = GreenNodeAgentBaseApp()
agent = MedievalStoryAgent()


@app.entrypoint
def handler(payload: dict[str, Any], context: RequestContext) -> dict[str, Any]:
    """Handle AgentBase POST /invocations requests."""
    try:
        story_request = agent.normalize_request(payload)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    llm_result = _write_with_llm(story_request)
    if llm_result["enabled"]:
        story_result = llm_result["result"]
    else:
        story_result = agent.write_story(story_request)

    return {
        "status": "success",
        "agent": "medieval_story_writer",
        "result": story_result,
        "llm": llm_result,
        "session_id": context.session_id,
    }


@app.ping
def health_check() -> PingStatus:
    """AgentBase health check for GET /health."""
    return PingStatus.HEALTHY


def _write_with_llm(story_request) -> dict[str, Any]:
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1")
    model = os.getenv("LLM_MODEL")

    if not api_key or not model:
        return {
            "enabled": False,
            "message": "Set LLM_API_KEY and LLM_MODEL to enable LLM story writing.",
        }

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=agent.llm_prompt(story_request),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.8")),
    )
    content = response.choices[0].message.content or "{}"

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {"title": "Medieval Story", "story": content, "outline": [], "metadata": {}}

    return {
        "enabled": True,
        "model": model,
        "result": parsed,
    }


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
