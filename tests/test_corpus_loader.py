"""Tests for CorpusLoader."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from ma_engine.corpus.loader import CorpusLoader


def _make_corpus(tmpdir: str, corpus_id: str = "c1", lines: list[str] | None = None) -> Path:
    root = Path(tmpdir) / corpus_id
    root.mkdir()
    (root / "manifest.json").write_text(json.dumps({
        "corpus_id": corpus_id,
        "persona_label": "M",
        "persona_name": "test",
        "sources": ["a.txt"],
        "line_count": len(lines or []),
        "notes": "test",
    }))
    text = "\n".join(lines or ["one", "two", "three"])
    (root / "a.txt").write_text(text + "\n")
    return root


def test_corpus_loads_lines():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_corpus(tmp, lines=["alpha", "beta", "gamma"])
        c = CorpusLoader(root)
        assert c.line_count == 3


def test_corpus_sample_returns_n_unique():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_corpus(tmp, lines=[f"line {i}" for i in range(20)])
        c = CorpusLoader(root)
        sample = c.sample(n=5, seed=42)
        assert len(sample) == 5
        assert len(set(sample)) == 5


def test_corpus_search_case_insensitive():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_corpus(tmp, lines=["Open AI mission", "for-profit conversion", "openness matters"])
        c = CorpusLoader(root)
        hits = c.search("open")
        assert len(hits) == 2


def test_corpus_missing_manifest_raises():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "nope"
        root.mkdir()
        (root / "a.txt").write_text("x\n")
        with pytest.raises(FileNotFoundError):
            CorpusLoader(root)


