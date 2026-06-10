"""Question bank for the interview Q&A agent."""

QUESTION_BANK = {
    "behavioral": [
        {
            "id": "beh-001",
            "question": "Tell me about a time you handled a difficult stakeholder.",
            "signals": ["situation", "action", "result", "communication", "stakeholder"],
            "tips": [
                "Use the STAR structure: situation, task, action, result.",
                "Include a measurable outcome or clear business impact.",
            ],
        },
        {
            "id": "beh-002",
            "question": "Describe a time you made a mistake and what you learned.",
            "signals": ["mistake", "owned", "learned", "changed", "prevent"],
            "tips": [
                "Show ownership without blaming others.",
                "Explain what process or behavior changed afterward.",
            ],
        },
    ],
    "technical": [
        {
            "id": "tech-001",
            "question": "How would you design a rate limiter for a payment API?",
            "signals": ["token bucket", "redis", "limit", "latency", "failure", "distributed"],
            "tips": [
                "Discuss algorithm choice and tradeoffs.",
                "Mention consistency, Redis/data store behavior, and failure modes.",
            ],
        },
        {
            "id": "tech-002",
            "question": "How do you debug a production latency spike?",
            "signals": ["metrics", "logs", "traces", "baseline", "rollback", "hypothesis"],
            "tips": [
                "Start with impact and scope before jumping into fixes.",
                "Use metrics, logs, and traces to validate hypotheses.",
            ],
        },
    ],
    "product": [
        {
            "id": "prod-001",
            "question": "How would you improve a mobile wallet onboarding flow?",
            "signals": ["funnel", "dropoff", "experiment", "user", "risk", "conversion"],
            "tips": [
                "Talk about measuring the funnel before proposing changes.",
                "Balance conversion improvements with fraud and compliance risk.",
            ],
        },
        {
            "id": "prod-002",
            "question": "How do you prioritize features when engineering capacity is limited?",
            "signals": ["impact", "effort", "risk", "data", "stakeholders", "tradeoff"],
            "tips": [
                "Make the prioritization framework explicit.",
                "Call out tradeoffs and how you would align stakeholders.",
            ],
        },
    ],
}
