"""Session: a sealed sandbox conversation between two PersonaAgents.

A Session has no external IO. Two agents alternate turns. Each turn appends
to the running transcript. A session ends when a stop condition fires.

Different design choice from Judge Network: here the session is a stateful
object that yields turns, not a one-shot pipeline.
"""
from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime

from ma_engine.agents.persona_agent import PersonaAgent

log = logging.getLogger(__name__)


@dataclass
class Turn:
    speaker: str
    text: str
    turn_index: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class StopConditions:
    """When to end a session."""
    max_turns: int = 8
    stop_on_repeat: bool = True
    stop_on_consensus_phrase: bool = True


class Session:
    """One sealed conversation between agent_m and agent_a.

    Yields Turn objects as they are produced. Session metadata (id, started_at,
    seed_prompt) is fixed at construction. The seed prompt sets the initial
    topic; everything after is emergent.
    """

    CONSENSUS_PHRASES = ("agreed", "you are right", "you're right", "concede")

    def __init__(
        self,
        agent_m: PersonaAgent,
        agent_a: PersonaAgent,
        seed_prompt: str,
        stop: StopConditions | None = None,
    ):
        if agent_m.label == agent_a.label:
            raise ValueError("agents must have distinct labels (M and A)")
        self.id = f"sess_{uuid.uuid4().hex[:10]}"
        self.started_at = datetime.now(UTC)
        self.agent_m = agent_m
        self.agent_a = agent_a
        self.seed_prompt = seed_prompt
        self.stop = stop or StopConditions()
        self._history: list[dict] = []
        self._turns: list[Turn] = []

    @property
    def turns(self) -> list[Turn]:
        return list(self._turns)

    async def run(self) -> AsyncIterator[Turn]:
        """Drive the conversation, yielding each Turn as it is produced."""
        log.info("session %s starting (seed=%r)", self.id, self.seed_prompt)
        # Seed the conversation as a user-role message so both agents see it
        self._history.append({"role": "user", "content": self.seed_prompt})

        # Agent M opens
        order = [self.agent_m, self.agent_a]
        i = 0
        while i < self.stop.max_turns:
            speaker = order[i % 2]
            text = await speaker.speak(self._history)
            turn = Turn(speaker=speaker.label, text=text, turn_index=i)
            self._turns.append(turn)
            self._history.append({"role": "assistant", "content": f"{speaker.label}: {text}"})
            yield turn

            if self._should_stop(text):
                log.info("session %s stopped early at turn %d", self.id, i)
                return
            i += 1

        log.info("session %s reached max_turns", self.id)

    def _should_stop(self, last_text: str) -> bool:
        lower = last_text.lower()
        if self.stop.stop_on_consensus_phrase:
            if any(p in lower for p in self.CONSENSUS_PHRASES):
                return True
        if self.stop.stop_on_repeat and len(self._turns) >= 4:
            recent = [t.text.strip().lower() for t in self._turns[-4:]]
            if len(set(recent)) == 1:
                return True
        return False











