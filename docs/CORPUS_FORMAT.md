# Corpus format

A persona corpus is a directory at `data/corpora/<corpus_id>/`. The directory contains a manifest and one or more text files of utterances.

## Manifest

`manifest.json`:

```json
{
  "corpus_id": "example_m",
  "persona_label": "M",
  "persona_name": "example persona m",
  "sources": ["quotes.txt", "interviews.txt"],
  "line_count": 1042,
  "notes": "Example corpus for tests. Replace with real material."
}
```

Required fields:
- `corpus_id` — unique short id, lowercase, snake_case
- `persona_label` — "M" or "A"
- `persona_name` — display name (free-form)
- `sources` — list of relative source files for provenance
- `line_count` — count of total lines across text files

## Text files

One utterance per line. Lowercase. No surrounding quote characters. No attribution. No timestamps in the line itself.

```
the foundation was a 501c3
i was in the room when the conversion was discussed
charters dont convert without unanimous board action
```

Multiple text files allowed. The loader concatenates them all.

## What to put in a corpus

For each persona, pull from public material:
- transcripts of interviews and podcast appearances
- official press statements
- public legal filings (when they're written in the persona's voice)
- social media posts

Avoid:
- material you can't link a public source for
- material that crosses defamation lines if quoted out of context
- non-public material of any kind

## What we ship

The repo ships only `example_m` and `example_a`, each with a small synthetic set of utterances. They exist for tests and CI. They are not real personas.

## Updating a corpus

Bump the line_count in the manifest. Add a note in CHANGELOG.md under a "data" subsection if the change is significant. The engine doesn't care about corpus version, but reproducing transcripts from old corpora is impossible if you overwrite them.



