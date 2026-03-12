"""Tests for Session and Turn behavior. Uses a stub backbone."""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from ma_engine.agents.persona_agent import PersonaAgent, PersonaConfig
from ma_engine.runtime.session import Session, StopConditions


@dataclass
class StubBackbone:
    name: str = "stub"
    canned: list = None

    def __post_init__(self):
        self._i = 0
        if self.canned is None:
            self.canned = [
                "i was in the room",
                "you were not in the room",
                "i have receipts",
                "your receipts are tweets",
                "this is a long con",
                "the foundation was a 501c3",
                "agreed.",
                "agreed.",
            ]

    async def complete(self, messages, temperature=0.7, max_tokens=256) -> str:
        out = self.canned[self._i % len(self.canned)]
        self._i += 1
        return out


def _agent(label: str, backbone: StubBackbone) -> PersonaAgent:
    cfg = PersonaConfig(
        label=label,
        persona_name=f"persona_{label.lower()}",
        corpus_id=f"corpus_{label.lower()}",
        system_prompt="you are persona " + label,
        backbone="openai",
        style_examples=["example one", "example two"],
    )
    return PersonaAgent(cfg, backbone=backbone)


@pytest.mark.asyncio
async def test_session_runs_to_max_turns():
    bb = StubBackbone(canned=["one", "two", "three", "four", "five", "six", "seven", "eight"])
    m = _agent("M", bb)
    a = _agent("A", bb)
    s = Session(m, a, seed_prompt="test", stop=StopConditions(max_turns=4, stop_on_consensus_phrase=False))
    turns = [t async for t in s.run()]
    assert len(turns) == 4
    assert turns[0].speaker == "M"
    assert turns[1].speaker == "A"


@pytest.mark.asyncio
async def test_session_stops_on_consensus_phrase():
    bb = StubBackbone(canned=["disagree", "agreed.", "extra"])
    m = _agent("M", bb)
    a = _agent("A", bb)
    s = Session(m, a, seed_prompt="test", stop=StopConditions(max_turns=8))
    turns = [t async for t in s.run()]
    assert len(turns) == 2  # M says "disagree", A says "agreed.", stops


@pytest.mark.asyncio
async def test_session_rejects_same_label_agents():
    bb = StubBackbone()
    m1 = _agent("M", bb)
    m2 = _agent("M", bb)
    with pytest.raises(ValueError):
        Session(m1, m2, seed_prompt="test")









