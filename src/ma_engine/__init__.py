"""M.A. Engine: two-agent sealed-sandbox simulation framework.

Loads paired persona corpora, runs alternating-turn dialogue between two
language model agents, and writes structured transcripts to disk.

The simulation has no external IO during a session. Agents see each other
and nothing else. Each session starts cold.
"""

from ma_engine._version import __version__
from ma_engine.agents.persona_agent import PersonaAgent
from ma_engine.corpus.loader import CorpusLoader
from ma_engine.runtime.scheduler import Scheduler
from ma_engine.runtime.session import Session

__all__ = [
    "Session",
    "Scheduler",
    "PersonaAgent",
    "CorpusLoader",
    "__version__",
]
