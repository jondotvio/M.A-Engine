"""Build PersonaAgents from corpus directories and a config file.

Lets the rest of the project treat agents as a config-driven thing rather
than instantiating PersonaAgent and PersonaConfig by hand everywhere.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ma_engine.agents.persona_agent import PersonaAgent, PersonaConfig
from ma_engine.corpus.loader import CorpusLoader


@dataclass
class PersonaSpec:
    label: str
    persona_name: str
    corpus_path: str
    backbone: str
    system_prompt: str
    temperature: float = 0.7
    max_tokens: int = 220
    style_anchor_count: int = 6


def load_persona_spec(path: Path | str) -> PersonaSpec:
    data = json.loads(Path(path).read_text())
    return PersonaSpec(**data)


def build_agent(spec: PersonaSpec, sample_seed: int | None = None) -> PersonaAgent:
    corpus = CorpusLoader(spec.corpus_path)
    style_examples = corpus.sample(spec.style_anchor_count, seed=sample_seed)
    config = PersonaConfig(
        label=spec.label,
        persona_name=spec.persona_name,
        corpus_id=corpus.manifest.corpus_id,
        system_prompt=spec.system_prompt,
        backbone=spec.backbone,
        temperature=spec.temperature,
        max_tokens=spec.max_tokens,
        style_examples=style_examples,
    )
    return PersonaAgent(config)


def build_pair(
    m_spec_path: Path | str,
    a_spec_path: Path | str,
    seed: int | None = None,
) -> tuple[PersonaAgent, PersonaAgent]:
    m_spec = load_persona_spec(m_spec_path)
    a_spec = load_persona_spec(a_spec_path)
    if m_spec.label != "M" or a_spec.label != "A":
        raise ValueError("first spec must be label 'M', second must be 'A'")
    return build_agent(m_spec, sample_seed=seed), build_agent(a_spec, sample_seed=seed)

