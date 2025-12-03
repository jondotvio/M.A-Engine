"""Scheduler: runs sessions at controlled intervals.

The scheduler picks a seed prompt from a rotating pool, constructs a fresh
Session, runs it, and writes the transcript via TranscriptWriter. After each
run, sleeps for the configured interval.

Intentionally simple. We don't use a third party scheduler because the
cadence is low (1-3 sessions per day in normal mode, faster in burst mode).
"""
from __future__ import annotations

import asyncio
import logging
import random
from dataclasses import dataclass

from ma_engine.agents.persona_agent import PersonaAgent
from ma_engine.logging.transcript_writer import TranscriptWriter
from ma_engine.runtime.session import Session, StopConditions

log = logging.getLogger(__name__)


@dataclass
class SchedulerConfig:
    interval_seconds: int = 6 * 60 * 60  # default: every 6 hours
    burst_mode: bool = False
    burst_interval_seconds: int = 30 * 60  # 30 min in burst
    max_turns_per_session: int = 8


class Scheduler:
    def __init__(
        self,
        agent_m: PersonaAgent,
        agent_a: PersonaAgent,
        seed_pool: list[str],
        writer: TranscriptWriter,
        config: SchedulerConfig | None = None,
    ):
        if not seed_pool:
            raise ValueError("seed_pool cannot be empty")
        self.agent_m = agent_m
        self.agent_a = agent_a
        self.seed_pool = list(seed_pool)
        self.writer = writer
        self.config = config or SchedulerConfig()
        self._stopped = asyncio.Event()
        self._sessions_completed = 0

    @property
    def sessions_completed(self) -> int:
        return self._sessions_completed

    def stop(self) -> None:
        log.info("scheduler stop requested")
        self._stopped.set()

    async def run_forever(self) -> None:
        log.info(
            "scheduler starting interval=%ds burst=%s",
            self._current_interval(), self.config.burst_mode,
        )
        while not self._stopped.is_set():
            try:
                await self._run_one_session()
            except Exception:
                log.exception("session failed")
            await self._sleep_or_stop(self._current_interval())

    async def run_once(self) -> str | None:
        """Run a single session and return its session id."""
        return await self._run_one_session()

    async def _run_one_session(self) -> str | None:
        seed = random.choice(self.seed_pool)
        stop = StopConditions(max_turns=self.config.max_turns_per_session)
        session = Session(self.agent_m, self.agent_a, seed_prompt=seed, stop=stop)
        async for _turn in session.run():
            pass
        path = self.writer.write(session)
        log.info("transcript written: %s", path)
        self._sessions_completed += 1
        return session.id

    def _current_interval(self) -> int:
        if self.config.burst_mode:
            return self.config.burst_interval_seconds
        return self.config.interval_seconds

    async def _sleep_or_stop(self, seconds: int) -> None:
        try:
            await asyncio.wait_for(self._stopped.wait(), timeout=seconds)
        except TimeoutError:
            return




