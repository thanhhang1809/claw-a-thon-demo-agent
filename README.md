# Medieval Story Writer Agent

Local/AgentBase agent for writing medieval fantasy stories.

## Features

- Writes medieval stories from a topic, prompt, or message.
- Supports tone controls: `epic`, `dark`, `romantic`, and `humorous`.
- Supports length controls: `short`, `medium`, and `long`.
- Runs locally without external API keys.
- Supports LLM-powered story writing on AgentBase with an OpenAI-compatible model.

## Quick start

```bash
python3 -m medieval_story_agent.cli "mot hiep si di tim vuong mien that lac"
```

Try a sample run:

```bash
python3 -m medieval_story_agent.cli "a cursed tower near the winter sea" --tone dark --length short
```

Available tones:

- `epic`
- `dark`
- `romantic`
- `humorous`

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
  "topic": "mot cong chua gia trai lam hiep si",
  "tone": "epic",
  "length": "medium",
  "protagonist": "cong chua Annelise",
  "setting": "vuong quoc da trang"
}
```

For LLM story writing, configure:

```bash
LLM_API_KEY=
LLM_BASE_URL=https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1
LLM_MODEL=
```
