# Changelog

## [0.6.1] - 2026-04-25
- fix: TranscriptWriter handled UTC offset incorrectly on cold-start days
- chore: bump grok default to grok-4 in backbones

## [0.6.0] - 2026-04-08
- feat: SchedulerConfig.burst_mode for high-cadence sessions
- feat: stop-on-repeat detection (4-turn rolling window)
- refactor: pull seeds out of Scheduler into runtime/seeds.py

## [0.5.2] - 2026-03-19
- fix: corpus manifest now requires explicit line_count
- chore: ruff cleanup pass

## [0.5.1] - 2026-03-04
- fix: PersonaAgent.render_system handled empty style_examples poorly
- docs: clarify what "sealed" means in the README

## [0.5.0] - 2026-02-12
- feat: builder.py for spec-driven agent construction
- breaking: PersonaConfig now requires explicit corpus_id

## [0.4.3] - 2026-01-22
- fix: TranscriptWriter date dirs were timezone-naive

## [0.4.2] - 2026-01-08
- chore: tighten test suite, add asyncio fixtures

## [0.4.1] - 2025-12-19
- fix: stop_on_consensus_phrase missed casing edge cases

## [0.4.0] - 2025-12-02
- feat: dual-format transcript output (json + txt)

## [0.3.0] - 2025-10-21
- feat: CorpusLoader, manifest format
- feat: spec files for PersonaAgent

## [0.2.0] - 2025-09-04
- feat: GrokBackbone added alongside OpenAIBackbone
- refactor: backbone protocol + base http class

## [0.1.0] - 2025-07-08
- initial: PersonaAgent + Session, single backbone (openai)
