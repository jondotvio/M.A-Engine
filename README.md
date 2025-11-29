# M.A. Engine

> A sealed two-agent simulation framework for paired persona modeling.

[![python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](#)
[![license MIT](https://img.shields.io/badge/license-MIT-green.svg)](#)
[![tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#)

`ma-engine` runs two language model agents in a sealed sandbox where the only thing each agent can do is talk to the other one. Each agent is built from a persona corpus: public utterances from a single subject, indexed and sampled as style anchors at session construction.

The engine is small. The premise is too. The interesting part is what the agents do with it.

## Quick start

```bash
git clone https://github.com/jondotvio/M.A-Engine.git
cd M.A-Engine
pip install -e ".[dev]"
```

Set credentials:

```bash
export OPENAI_API_KEY="..."
export XAI_API_KEY="..."
```

Run a single session:

```bash
ma-engine run-once \
    --m-spec data/personas/m.json \
    --a-spec data/personas/a.json \
    --turns 8
```

Or run continuously:

```bash
ma-engine run-loop \
    --m-spec data/personas/m.json \
    --a-spec data/personas/a.json \
    --interval 21600
```

Transcripts go to `data/transcripts/<date>/<session_id>.txt`.

## Why "sealed"

Most multi-agent frameworks let agents call tools, read files, search the web. M.A. Engine does not. Each session is a clean, no-IO conversation between two persona-conditioned agents and a single seed prompt. There is no memory between sessions. There is no scratchpad. There is no retrieval.

The constraint is the experiment. We want to see what comes out of two opposed personas with nothing else to lean on.

## Architecture

```
            ┌───────────────────────────────────────────────────┐
            │                    Scheduler                       │
            │  (rotates seeds, starts sessions on a cadence)    │
            └────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
            ┌───────────────────────────────────────────────────┐
            │                     Session                        │
            │   sealed conversation, alternating turns           │
            │   max_turns + stop conditions                      │
            └─────┬───────────────────────────────────┬─────────┘
                  │                                   │
                  ▼                                   ▼
       ┌─────────────────────┐               ┌─────────────────────┐
       │   PersonaAgent M    │               │   PersonaAgent A    │
       │   backbone: openai  │               │   backbone: grok    │
       │   corpus_id: m_corp │               │   corpus_id: a_corp │
       └──────────┬──────────┘               └──────────┬──────────┘
                  │                                     │
                  └──────────────┬──────────────────────┘
                                 ▼
                      ┌─────────────────────┐
                      │ TranscriptWriter    │
                      │ json + txt per run  │
                      └─────────────────────┘
```

## Layout

```
src/ma_engine/
    agents/         PersonaAgent, backbones, builder
    runtime/        Session, Scheduler, seeds
    corpus/         CorpusLoader and manifest format
    logging/        TranscriptWriter, log setup
    cli/            ma-engine entrypoint
tests/              pytest suite
data/
    corpora/        persona corpora (NOT committed, see notes)
    transcripts/    session output
notebooks/          experimental analysis
docs/               extended notes
```

## Persona corpora

A corpus is a directory:

```
data/corpora/<corpus_id>/
    manifest.json
    quotes.txt        # 1 utterance per line
    interviews.txt    # optional, longer-form
    posts.txt         # optional, social
```

The repo ships only example/test corpora. Full persona corpora are not redistributed: collect public material yourself, document sources in the manifest, and you're set.

## Backbones

Two are wired up:

- `openai` (gpt-4o by default)
- `grok` (grok-4 by default)

Adding a new one is one class implementing `Backbone.complete(messages, temperature, max_tokens) -> str`.

## Tests

```bash
pytest -v
```

## Notes

- Output style is short, lowercase, no preamble. This is a deliberate constraint applied via system prompt. It also makes transcripts more interesting to read.
- Sessions stop early on consensus phrases ("agreed", "you are right", etc) and on repeat-loop detection. In practice we rarely hit consensus.
- Backbone choice can be swapped per-agent. M on openai + A on grok produces different dynamics than the symmetric case.

## License

MIT.










