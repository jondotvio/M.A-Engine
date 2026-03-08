# Design notes

## Why two agents

A single LLM with a persona prompt is a generation tool. Two LLMs with opposed persona prompts in conversation is a dynamic system. The output is no longer just "what would persona X say in isolation" but "what does the boundary look like where persona X meets persona Y." That boundary is where the experiment lives.

We tried single-agent Q+A and four-agent panels first. Two is the right number. With one, there's no friction. With four, the conversation diffuses; agents pile on or drift toward majority. Two stays clean.

## Why sealed

External tools, retrieval, or web access would let agents "win" arguments by retrieving facts. The point is to see what the persona corpus alone produces. If an agent can't make a point from its corpus, it can't make the point. That's the constraint and that's the data.

## Why short turns

We capped turns at 1-3 lines, lowercase, no preamble. Longer outputs collapse into LLM voice (hedges, qualifiers, "It's worth noting that..."). The short-turn constraint forces the agent to use clipped, declarative phrasings closer to actual transcript-of-conversation style. It also means the persona corpus has more weight per token.

## Stop conditions

Three stop conditions:

1. `max_turns` reached. Default 8. We don't go longer because by turn 9 the conversation usually loops.
2. consensus phrase detected. Rare. We track when it does happen (see `notes/consensus_log.md`).
3. repeat-loop detected. 4-turn window of identical text. Catches degenerate states where one agent gets stuck.

## Cold sessions

Each session starts cold. There is no shared memory, no profile evolution, no learned dynamic between the two agents. We do this on purpose. The question we want to answer is "what happens when corpus M meets corpus A on topic X" not "what happens when these two specific agent instances develop a relationship over 1000 sessions."

If we wanted the latter, we'd add memory. We don't, yet. Possibly v0.8.

## Backbone choice per agent

A subtle thing: putting agent M on grok and agent A on openai produces noticeably different transcripts than the symmetric case. The backbone's own tendencies (verbosity, hedging, certainty) interact with the persona prompt. We have not characterized this rigorously, but the asymmetric configuration tends to produce sharper exchanges.

Default config is asymmetric: M on openai, A on grok.

## Seed prompts

Seeds are intentionally short and declarative, not questions. Questions invite explanation. Declaratives invite agreement or disagreement, which is where the friction lives. "the conversion was lawful" produces better transcripts than "was the conversion lawful?"

The seed pool rotates randomly per session. Eventually we want a more thoughtful seed scheduler that pairs seeds to news cycles, but for now the pool is static.

## Things we considered and didn't ship

- **Model temperature ramping.** Tested. Didn't help.
- **Persona-conditioned backbones.** Fine-tuning instead of prompting. Out of scope for the engine.
- **Multi-language sessions.** Possible but corpus collection becomes a much bigger project.
- **A judge agent that scores who "won" the session.** Too easy to bias. Skipped.





