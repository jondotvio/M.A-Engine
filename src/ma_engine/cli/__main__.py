"""ma-engine CLI."""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from ma_engine.agents.builder import build_pair
from ma_engine.logging.setup import configure as configure_logging
from ma_engine.logging.transcript_writer import TranscriptWriter
from ma_engine.runtime.scheduler import Scheduler, SchedulerConfig
from ma_engine.runtime.seeds import load_seeds


def cmd_run_once(args: argparse.Namespace) -> int:
    agent_m, agent_a = build_pair(args.m_spec, args.a_spec, seed=args.seed)
    seeds = load_seeds(args.seeds)
    writer = TranscriptWriter(root=args.out)
    scheduler = Scheduler(
        agent_m, agent_a, seeds, writer,
        SchedulerConfig(max_turns_per_session=args.turns),
    )
    sid = asyncio.run(scheduler.run_once())
    print(f"session: {sid}")
    return 0


def cmd_run_loop(args: argparse.Namespace) -> int:
    agent_m, agent_a = build_pair(args.m_spec, args.a_spec)
    seeds = load_seeds(args.seeds)
    writer = TranscriptWriter(root=args.out)
    cfg = SchedulerConfig(
        interval_seconds=args.interval,
        burst_mode=args.burst,
        max_turns_per_session=args.turns,
    )
    scheduler = Scheduler(agent_m, agent_a, seeds, writer, cfg)
    try:
        asyncio.run(scheduler.run_forever())
    except KeyboardInterrupt:
        scheduler.stop()
        print(f"\nstopped. completed sessions: {scheduler.sessions_completed}")
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    transcript = Path(args.path)
    if not transcript.exists():
        print(f"file not found: {transcript}", file=sys.stderr)
        return 2
    print(transcript.read_text())
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ma-engine")
    p.add_argument("--log-level", default="INFO")
    sub = p.add_subparsers(dest="cmd", required=True)

    once = sub.add_parser("run-once", help="run a single session")
    once.add_argument("--m-spec", required=True)
    once.add_argument("--a-spec", required=True)
    once.add_argument("--seeds", default=None)
    once.add_argument("--out", default="data/transcripts")
    once.add_argument("--turns", type=int, default=8)
    once.add_argument("--seed", type=int, default=None, help="random seed for style sampling")
    once.set_defaults(func=cmd_run_once)

    loop = sub.add_parser("run-loop", help="run sessions on a cadence")
    loop.add_argument("--m-spec", required=True)
    loop.add_argument("--a-spec", required=True)
    loop.add_argument("--seeds", default=None)
    loop.add_argument("--out", default="data/transcripts")
    loop.add_argument("--turns", type=int, default=8)
    loop.add_argument("--interval", type=int, default=21600)
    loop.add_argument("--burst", action="store_true")
    loop.set_defaults(func=cmd_run_loop)

    inspect = sub.add_parser("inspect", help="print a transcript")
    inspect.add_argument("path")
    inspect.set_defaults(func=cmd_inspect)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.log_level)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())



