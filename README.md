# claw-a-thon-demo-agent

Local Interview Q&A agent for practicing behavioral, technical, and product interview answers.

## Features

- Generates interview questions by category.
- Scores answers with a lightweight rubric.
- Highlights matched and missing interview signals.
- Gives concrete feedback and sample answers.
- Runs locally without external API keys.
- Supports LLM-powered coaching on AgentBase with an OpenAI-compatible model.

## Quick start

```bash
python3 -m interview_agent.cli --category behavioral
```

Try a sample run:

```bash
python3 -m interview_agent.cli --category technical --sample
```

Available categories:

- `behavioral`
- `technical`
- `product`

## Run tests

```bash
python3 -m unittest discover
```

## AgentBase runtime

The AgentBase entrypoint is `main.py`. It exposes:

- `GET /health`
- `POST /invocations`

Example request body:

```json
{
  "category": "technical",
  "answer": "I would use a token bucket in Redis and monitor latency..."
}
```

For LLM coaching, configure:

```bash
LLM_API_KEY=
LLM_BASE_URL=https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1
LLM_MODEL=
```
