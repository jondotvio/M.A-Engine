"""Seed prompt pool for sessions.

Seeds are the topic openers passed to the conversation as the first user
message. The agents take it from there. Seeds are intentionally vague to
give the agents room to argue.
"""
from __future__ import annotations

DEFAULT_SEEDS: list[str] = [
    "what was the original mission",
    "explain the conversion in your own words",
    "who has standing here",
    "the foundation was a 501c3",
    "the deposit was paid in good faith",
    "the discovery will determine the outcome",
    "you cannot serve two charters",
    "the board acted unilaterally",
    "the board acted within its authority",
    "the corpus says otherwise",
    "the press release contradicts the filing",
    "you signed the email chain",
    "you departed before the vote",
    "you departed after the vote",
    "compute is not the issue, governance is",
    "compute is the entire issue",
    "the agreement was written down",
    "the agreement was understood",
    "you misremember the room",
    "i was in the room",
]


def load_seeds(path: str | None = None) -> list[str]:
    if path is None:
        return list(DEFAULT_SEEDS)
    with open(path) as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
