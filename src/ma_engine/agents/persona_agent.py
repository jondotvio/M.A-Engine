"""PersonaAgent: a single language agent with a fixed persona prompt.

Wraps a chat model and a corpus reference. Each agent has its own backbone
(grok or gpt) selected at construction. Stateless across turns within a
session except for the conversation history that gets passed in.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

from ma_engine.agents.backbones import Backbone, GrokBackbone, OpenAIBackbone

log = logging.getLogger(__name__)


PersonaLabel = Literal["M", "A"]


@dataclass
class PersonaConfig:
    label: PersonaLabel
    persona_name: str
    corpus_id: str
    system_prompt: str
    backbone: str = "openai"
    temperature: float = 0.7
    max_tokens: int = 220
    style_examples: list[str] = field(default_factory=list)


class PersonaAgent:
    """A single agent in the simulation.

    Builds a system prompt from the persona config plus a small number of
    style-anchoring example utterances drawn from the corpus.
    """

    def __init__(self, config: PersonaConfig, backbone: Backbone | None = None):
        self.config = config
        self._backbone = backbone or self._build_backbone(config.backbone)

    @staticmethod
    def _build_backbone(name: str) -> Backbone:
        if name == "grok":
            return GrokBackbone()
        if name == "openai":
            return OpenAIBackbone()
        raise ValueError(f"unknown backbone: {name}")

    @property
    def label(self) -> PersonaLabel:
        return self.config.label

    def render_system(self) -> str:
        anchors = "\n".join(f"- {line}" for line in self.config.style_examples[:6])
        return (
            f"{self.config.system_prompt}\n\n"
            f"Style anchors from your corpus:\n{anchors}\n\n"
            f"Respond in 1-3 short lines, lowercase, no preamble. "
            f"Do not narrate, do not roleplay, do not break character."
        )

    async def speak(self, history: list[dict]) -> str:
        """Produce the next utterance given the conversation history."""
        messages = [{"role": "system", "content": self.render_system()}]
        messages.extend(history)
        text = await self._backbone.complete(
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return text.strip()

    def __repr__(self) -> str:
        return f"PersonaAgent(label={self.config.label}, backbone={self.config.backbone})"




