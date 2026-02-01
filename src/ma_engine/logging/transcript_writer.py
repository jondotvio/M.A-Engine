"""TranscriptWriter: serializes a completed Session to disk.

Writes two artifacts per session:

    data/transcripts/<YYYY-MM-DD>/<session_id>.json   structured record
    data/transcripts/<YYYY-MM-DD>/<session_id>.txt    human-readable

The text version is what gets posted to X. The JSON is the source of truth
for replays and analytics.
"""
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from ma_engine.runtime.session import Session

log = logging.getLogger(__name__)


class TranscriptWriter:
    def __init__(self, root: Path | str = "data/transcripts"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, session: Session) -> Path:
        day_dir = self.root / session.started_at.strftime("%Y-%m-%d")
        day_dir.mkdir(parents=True, exist_ok=True)
        json_path = day_dir / f"{session.id}.json"
        txt_path = day_dir / f"{session.id}.txt"
        json_path.write_text(self._render_json(session))
        txt_path.write_text(self._render_text(session))
        return txt_path

    def _render_json(self, session: Session) -> str:
        payload = {
            "session_id": session.id,
            "started_at": session.started_at.isoformat(),
            "ended_at": datetime.now(UTC).isoformat(),
            "seed_prompt": session.seed_prompt,
            "agents": {
                "M": {
                    "label": session.agent_m.label,
                    "backbone": session.agent_m.config.backbone,
                    "corpus_id": session.agent_m.config.corpus_id,
                },
                "A": {
                    "label": session.agent_a.label,
                    "backbone": session.agent_a.config.backbone,
                    "corpus_id": session.agent_a.config.corpus_id,
                },
            },
            "turns": [
                {
                    "index": t.turn_index,
                    "speaker": t.speaker,
                    "text": t.text,
                    "timestamp": t.timestamp.isoformat(),
                }
                for t in session.turns
            ],
        }
        return json.dumps(payload, indent=2)

    def _render_text(self, session: Session) -> str:
        ts = session.started_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        header = f"TRANSCRIPT {session.id} / sandbox.local\n{ts}\n\n"
        body = "\n".join(f"{t.speaker}: {t.text}" for t in session.turns)
        return f"{header}{body}\n\nend of segment.\n"





