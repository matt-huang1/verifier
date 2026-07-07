# ADR-0001: Deterministic verification, not LLM judging

- **Status:** Accepted
- **Date:** 2026-07-07

## Context

The failure this project exists to prevent is a model re-asserting its own output and
that re-assertion being mistaken for a check. An earlier AI-assisted research task
produced a plausible claim not grounded in its cited source; asking the model to check
itself did not catch it — going back to the primary source did.

The tempting shortcut for a citation verifier is to pass the claim, the source text,
and the question "does this support that?" to an LLM and return its answer. That
reintroduces exactly the failure mode: a generative model grading a generative claim.

## Decision

Deterministic code issues every verdict. Where an LLM is used at all, it only ever
*proposes* or *locates* (e.g. surfacing candidate supporting sentences); the final
call is made by deterministic rules — quote matching, entity/number comparison —
against the independently fetched source. No module lets a model grade its own output.

## Consequences

- The reliable core (quote presence, numeric/date/entity agreement) is fully
  deterministic and reproducible, and can be adversarially tested.
- Cases that genuinely require judgement are reported as such and left to a human,
  rather than being papered over with a confident machine verdict.
- Recall is lower than an "ask the LLM" approach would appear to give — accepted
  deliberately (see 0003).

## Alternatives considered

- **LLM-as-judge.** Rejected: it is the failure mode, not a fix for it.
- **LLM-as-extractor, deterministic decision.** Accepted as the *only* sanctioned role
  for a generative model here, and even then gated behind deterministic checks.
