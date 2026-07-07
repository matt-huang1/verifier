# ADR-0004: verify_citation first; check_source is next, not cut

- **Status:** Accepted
- **Date:** 2026-07-07

## Context

A "brutally small V1" argument says: cut everything except `verify_citation` — no
source authenticity at all. That is right about ruthless scoping but wrong about *what*
to cut. Source authenticity (spoofed / lookalike / typosquatted domains) is the one
capability here that isn't "another does-the-source-support-the-claim checker" — it is
the differentiator, and it comes from a real, previously caught spoofing bug.

Separately, the existing domain check is **allowlist-based**: it decides legitimacy
against a caller-supplied list of known-good domains. The generic MCP case has no
allowlist — authenticity has to be judged against the domain *implied by the claim*
(homograph and near-miss detection relative to an expected domain). That is genuinely
new design work, not a straight port.

## Decision

Ship `verify_citation` first — it is ~80% assembly of parts already proven (fetch,
extract, quote match, entity check). Ship `check_source` immediately after as the next
tool, with its allowlist-free authenticity design treated as first-class work (its own
ADR when designed), not a shim.

Do **not** cut `check_source` from the roadmap to satisfy minimalism. Minimalism
applies to the *first shippable slice*, not to the project's distinctive capability.

## Consequences

- Fastest path to a working, demoable tool (verify_citation) without amputating the
  differentiator.
- `check_source`'s "expected domain" design is scheduled deliberately rather than
  discovered late.

## Alternatives considered

- **Cut check_source entirely from V1 scope.** Rejected: removes the one uniquely-ours
  capability.
- **Ship both simultaneously.** Rejected: check_source needs design (the allowlist-free
  case); blocking verify_citation on it delays the demo.
