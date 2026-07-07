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

The bar is not "no ML." Any component in the **judgment path** must be (1) reproducible,
(2) traceable, and (3) have known, bounded failure modes. Three kinds of component sit
differently against that bar:

- **Deterministic rules** — quote matching, entity/number comparison against the
  independently fetched source — meet all three. They are the sanctioned default and
  issue every V1 verdict.
- **A fixed-weight NLI model** is reproducible (same input → same output) but trades
  *rule-level* traceability for a model error profile: you can characterise its failures
  statistically but not point to the rule that fired. That is a deliberate, measured,
  lower-assurance choice — permitted only via a future ADR that owns the trade-off, not
  banned outright.
- **A generative LLM freely emitting verdicts** fails all three — not reproducible, not
  traceable, unbounded failure modes — and is the failure mode this project exists to
  prevent. It stays prohibited in the judgment path.

Where an LLM is used at all, it only ever *proposes* or *locates* (e.g. surfacing
candidate supporting sentences); the final call is made against the fetched source by a
component that clears the bar above. No module lets a model grade its own output.

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
  for a *generative* model here, and even then gated behind deterministic checks.
- **NLI (entailment) model for semantic support.** Deferred, not rejected: it is
  discriminative rather than generative and is reproducible, so it is governed by the
  Decision's three-part bar (reproducible / traceable / bounded failure modes), not the
  generative-role prohibition. Its tradeoff — semantic-drift detection at the cost of
  rule-level traceability — earns its own ADR if adopted.
