"""CorpusLoader: loads a persona corpus from disk and surfaces sample lines.

A corpus is a directory containing newline-separated quote files. The loader
indexes them, tracks counts, and serves random samples for use as style
anchors in PersonaAgent system prompts.

The actual training data is NOT shipped in the repo. The repo includes
small example corpora for testing and CI.
"""
from __future__ import annotations

import json
import logging
import random
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


@dataclass
class CorpusManifest:
    corpus_id: str
    persona_label: str
    persona_name: str
    sources: list[str]
    line_count: int
    notes: str = ""


class CorpusLoader:
    """Loads a persona corpus directory.

    Expected layout:

        data/corpora/<corpus_id>/
            manifest.json
            quotes.txt          # one utterance per line, lowercase, no quotes
            interviews.txt      # optional, longer-form
            posts.txt           # optional, social media style

    The loader concatenates all *.txt files into a single in-memory list.
    """

    def __init__(self, root: Path | str):
        self.root = Path(root)
        if not self.root.exists():
            raise FileNotFoundError(f"corpus dir does not exist: {self.root}")
        self.manifest = self._load_manifest()
        self._lines: list[str] = self._load_lines()
        log.info(
            "corpus '%s' loaded: %d lines from %d files",
            self.manifest.corpus_id, len(self._lines), len(self.manifest.sources),
        )

    def _load_manifest(self) -> CorpusManifest:
        path = self.root / "manifest.json"
        if not path.exists():
            raise FileNotFoundError(f"missing manifest.json in {self.root}")
        data = json.loads(path.read_text())
        return CorpusManifest(**data)

    def _load_lines(self) -> list[str]:
        out: list[str] = []
        for txt_file in sorted(self.root.glob("*.txt")):
            content = txt_file.read_text().splitlines()
            out.extend(line.strip() for line in content if line.strip())
        return out

    @property
    def line_count(self) -> int:
        return len(self._lines)

    def sample(self, n: int = 6, seed: int | None = None) -> list[str]:
        rng = random.Random(seed) if seed is not None else random
        n = min(n, len(self._lines))
        return rng.sample(self._lines, n)

    def search(self, keyword: str, limit: int = 20) -> list[str]:
        keyword = keyword.lower()
        hits = [line for line in self._lines if keyword in line.lower()]
        return hits[:limit]


