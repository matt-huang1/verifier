# ADR-0003: No confidence float — the status vocabulary carries epistemic state

- **Status:** Accepted
- **Date:** 2026-07-07

## Context

An early draft of the verdict schema carried `confidence: float` (0–1) alongside the
status. A numeric confidence on a deterministic verifier is a judgement wearing a
number: `0.87` implies a calibrated probability the system does not actually have, and
invites callers to threshold on a value that means nothing precise. It quietly
reintroduces the soft, ungrounded judgement this project is built to refuse.

## Decision

Remove the numeric confidence field entirely. Epistemic state is expressed through a
small, precise, evidence-backed **status vocabulary** — the statuses *are* the honest
discrete labels. For `verify_citation`:

- `supported` — the source contains the claim's substance; quote and/or entities agree.
- `contradicted` — the source states something incompatible (e.g. claim says 2035,
  source says 2050).
- `not_found_in_source` — the source does not contain support either way. This is the
  honest "couldn't confirm" answer, not a soft "probably not."
- `source_unreachable` — fetch/extraction failed; nothing was checked. Never collapsed
  into `not_found_in_source`.

Each status is defined by concrete evidence, so it is auditable and testable. "How sure
are you?" is answered by *which status* and *what evidence*, not by a number.

## Open sub-question (resolve in 0005, the contract ADR)

Whether a coarse qualitative band (e.g. exact-quote-match vs fuzzy-match) is also worth
surfacing *as a property of the evidence* (not a global confidence field). Current lean:
let the evidence objects carry match quality (e.g. `match_kind: exact | normalized |
fuzzy`) so the signal exists without a top-level "confidence" that gets thresholded.

## Consequences

- No caller can threshold on a made-up probability; they must read the status and its
  evidence.
- The demo reads cleanly: a status plus the exact mismatched figure, no "0.87" to
  explain.
- `partially_supported` is deliberately deferred from the V1 status set to keep it
  brutally small; revisit once real runs show a need it, not before.

## Alternatives considered

- **Keep the float.** Rejected: false precision, off-thesis.
- **Discrete confidence labels as a separate field (`high`/`low`).** Rejected as a
  top-level field: it is a smaller version of the same problem (a judgement label
  detached from evidence). Folded into the status vocabulary and, where useful, into
  per-evidence match quality instead.
