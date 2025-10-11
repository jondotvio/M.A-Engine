"""Tests for TranscriptWriter output format."""
from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime

from ma_engine.agents.persona_agent import PersonaAgent, PersonaConfig
from ma_engine.logging.transcript_writer import TranscriptWriter
from ma_engine.runtime.session import Session, Turn


@dataclass
class _Stub:
    name: str = "stub"
    async def complete(self, messages, temperature=0.7, max_tokens=256) -> str:
        return "ok"


def _agent(label: str) -> PersonaAgent:
    return PersonaAgent(
        PersonaConfig(
            label=label, persona_name="x", corpus_id="cx",
            system_prompt="x", backbone="openai", style_examples=[],
        ),
        backbone=_Stub(),
    )


def _make_session_with_turns():
    s = Session(_agent("M"), _agent("A"), seed_prompt="seed")
    s._turns = [
        Turn(speaker="M", text="hello", turn_index=0, timestamp=datetime.now(UTC)),
        Turn(speaker="A", text="no", turn_index=1, timestamp=datetime.now(UTC)),
    ]
    return s


def test_transcript_writer_creates_both_files():
    s = _make_session_with_turns()
    with tempfile.TemporaryDirectory() as tmp:
        w = TranscriptWriter(root=tmp)
        txt_path = w.write(s)
        json_path = txt_path.with_suffix(".json")
        assert txt_path.exists()
        assert json_path.exists()


def test_transcript_text_format_has_header_and_footer():
    s = _make_session_with_turns()
    with tempfile.TemporaryDirectory() as tmp:
        w = TranscriptWriter(root=tmp)
        txt_path = w.write(s)
        text = txt_path.read_text()
        assert "TRANSCRIPT" in text
        assert "sandbox.local" in text
        assert text.strip().endswith("end of segment.")


def test_transcript_json_has_session_metadata():
    s = _make_session_with_turns()
    with tempfile.TemporaryDirectory() as tmp:
        w = TranscriptWriter(root=tmp)
        txt_path = w.write(s)
        data = json.loads(txt_path.with_suffix(".json").read_text())
        assert data["session_id"] == s.id
        assert len(data["turns"]) == 2
        assert data["turns"][0]["speaker"] == "M"

